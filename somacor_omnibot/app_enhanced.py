_enhanced.py para usar Redis en la gestión de sesiones
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from flask_cors import CORS
import os
import requests
import re
from datetime import datetime
from session_manager import RedisSessionManager

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Permitir todas las origenes por ahora, ajustar para producción

# Configuración de la API del CMMS
CMMS_API_BASE_URL = os.environ.get('CMMS_API_BASE_URL', 'http://localhost:8000/api/')

# Gestor de sesiones de Redis
session_manager = RedisSessionManager()

class ConversationState:
    IDLE = 'idle'
    REPORTING_FAULT = 'reporting_fault'
    AWAITING_EQUIPMENT = 'awaiting_equipment'
    AWAITING_DESCRIPTION = 'awaiting_description'
    AWAITING_PRIORITY = 'awaiting_priority'
    CONFIRMING_REPORT = 'confirming_report'
    QUERYING_OT = 'querying_ot'

def get_user_session(user_id):
    session = session_manager.get_session(user_id)
    if not session:
        session = {
            'state': ConversationState.IDLE,
            'data': {}
        }
        session_manager.save_session(user_id, session)
    return session

def reset_user_session(user_id):
    session_manager.delete_session(user_id)

def get_equipos():
    try:
        response = requests.get(f'{CMMS_API_BASE_URL}equipos/', timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error al obtener equipos: {str(e)}")
        return []

def get_equipo_by_name_or_code(search_term):
    equipos = get_equipos()
    search_term = search_term.lower().strip()
    
    for equipo in equipos:
        nombre = equipo.get('nombreequipo', '').lower()
        codigo = str(equipo.get('codigointerno', '')).lower()
        
        if search_term in nombre or search_term in codigo:
            return equipo
    
    return None

def get_orden_trabajo(numero_ot):
    try:
        response = requests.get(f'{CMMS_API_BASE_URL}ordenes-trabajo/', timeout=5)
        if response.status_code == 200:
            ordenes = response.json()
            for orden in ordenes:
                if orden.get('numeroot', '').lower() == numero_ot.lower():
                    return orden
        return None
    except Exception as e:
        print(f"Error al obtener orden de trabajo: {str(e)}")
        return None

def create_fault_report(equipo_id, descripcion, prioridad='Media'):
    try:
        usuarios_response = requests.get(f'{CMMS_API_BASE_URL}users/', timeout=5)
        if usuarios_response.status_code != 200:
            return None, "No se pudo obtener información de usuarios"
        
        usuarios = usuarios_response.json()
        if not usuarios:
            return None, "No hay usuarios disponibles en el sistema"
        
        solicitante_id = usuarios[0]['id']
        
        data = {
            'idequipo': equipo_id,
            'descripcionproblemareportado': descripcion,
            'prioridad': prioridad,
            'idsolicitante': solicitante_id
        }
        
        response = requests.post(
            f'{CMMS_API_BASE_URL}ordenes-trabajo/reportar-falla/',
            json=data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            return response.json(), None
        else:
            return None, f"Error al crear el reporte: {response.text}"
            
    except Exception as e:
        print(f"Error al crear reporte de falla: {str(e)}")
        return None, f"Error de conexión: {str(e)}"

def format_orden_trabajo_info(orden):
    numero = orden.get('numeroot', 'N/A')
    estado = orden.get('estado_nombre', 'N/A')
    equipo = orden.get('equipo_nombre', 'N/A')
    tipo = orden.get('tipo_mantenimiento_nombre', 'N/A')
    prioridad = orden.get('prioridad', 'N/A')
    fecha_emision = orden.get('fechaemision', 'N/A')
    fecha_ejecucion = orden.get('fechaejecucion', 'No programada')
    tecnico = orden.get('tecnico_asignado_nombre', 'No asignado')
    
    mensaje = f"📋 *Orden de Trabajo: {numero}*\n\n"
    mensaje += f"🔧 Equipo: {equipo}\n"
    mensaje += f"📊 Estado: {estado}\n"
    mensaje += f"🔨 Tipo: {tipo}\n"
    mensaje += f"⚠️ Prioridad: {prioridad}\n"
    mensaje += f"📅 Fecha Emisión: {fecha_emision}\n"
    mensaje += f"🗓️ Fecha Ejecución: {fecha_ejecucion}\n"
    mensaje += f"👷 Técnico: {tecnico}\n"
    
    if orden.get('descripcionproblemareportado'):
        mensaje += f"\n📝 Problema: {orden.get('descripcionproblemareportado')}\n"
    
    return mensaje

def process_message(user_id, message):
    session = get_user_session(user_id)
    state = session['state']
    message_lower = message.lower().strip()
    
    if message_lower in ['cancelar', 'salir', 'reiniciar']:
        reset_user_session(user_id)
        return "❌ Operación cancelada. ¿En qué más puedo ayudarte?"
    
    if message_lower in ['ayuda', 'help', '?']:
        return (
            "🤖 *Asistente Virtual de Somacor-CMMS*\n\n"
            "Puedo ayudarte con:\n\n"
            "1️⃣ *Reportar una falla*\n"
            "   Escribe: 'reportar falla' o 'falla'\n\n"
            "2️⃣ *Consultar estado de OT*\n"
            "   Escribe: 'estado OT-XXX' o 'consultar OT-XXX'\n\n"
            "3️⃣ *Ver equipos*\n"
            "   Escribe: 'equipos' o 'listar equipos'\n\n"
            "También puedes escribir 'cancelar' en cualquier momento para reiniciar."
        )
    
    if state == ConversationState.IDLE:
        if 'hola' in message_lower or 'buenos' in message_lower or 'buenas' in message_lower:
            return (
                "¡Hola! 👋 Soy el asistente virtual de Somacor-CMMS.\n\n"
                "¿En qué puedo ayudarte hoy?\n\n"
                "• Reportar una falla\n"
                "• Consultar estado de una OT\n"
                "• Ver equipos disponibles\n\n"
                "Escribe 'ayuda' para ver más opciones."
            )
        
        elif 'reportar' in message_lower and 'falla' in message_lower:
            session['state'] = ConversationState.AWAITING_EQUIPMENT
            session['data'] = {}
            session_manager.save_session(user_id, session)
            return (
                "🔧 *Reporte de Falla*\n\n"
                "Por favor, indícame el nombre o código del equipo que presenta la falla.\n\n"
                "Ejemplo: 'Excavadora 01' o 'EXC-001'"
            )
        
        elif 'estado' in message_lower or 'consultar' in message_lower:
            ot_match = re.search(r'OT-[\w-]+', message, re.IGNORECASE)
            if ot_match:
                numero_ot = ot_match.group(0)
                orden = get_orden_trabajo(numero_ot)
                
                if orden:
                    return format_orden_trabajo_info(orden)
                else:
                    return f"❌ No se encontró la orden de trabajo '{numero_ot}'. Verifica el número e intenta nuevamente."
            else:
                session['state'] = ConversationState.QUERYING_OT
                session_manager.save_session(user_id, session)
                return (
                    "🔍 *Consulta de Orden de Trabajo*\n\n"
                    "Por favor, indícame el número de la OT que deseas consultar.\n\n"
                    "Ejemplo: 'OT-CORR-123' o 'OT-PREV-456'"
                )
        
        elif 'equipos' in message_lower or 'listar' in message_lower:
            equipos = get_equipos()
            if equipos:
                mensaje = "📋 *Equipos Disponibles:*\n\n"
                for i, equipo in enumerate(equipos[:10], 1):
                    nombre = equipo.get('nombreequipo', 'N/A')
                    codigo = equipo.get('codigointerno', 'N/A')
                    estado = equipo.get('estado_nombre', 'N/A')
                    mensaje += f"{i}. {nombre} ({codigo}) - {estado}\n"
                
                if len(equipos) > 10:
                    mensaje += f"\n... y {len(equipos) - 10} equipos más."
                
                return mensaje
            else:
                return "❌ No se pudieron obtener los equipos. Intenta más tarde."
        
        else:
            return (
                "🤔 No entendí tu mensaje.\n\n"
                "Puedes decir:\n"
                "• 'reportar falla'\n"
                "• 'estado OT-XXX'\n"
                "• 'equipos'\n"
                "• 'ayuda'\n"
            )
    
    elif state == ConversationState.AWAITING_EQUIPMENT:
        equipo = get_equipo_by_name_or_code(message)
        
        if equipo:
            session['data']['equipo'] = equipo
            session['state'] = ConversationState.AWAITING_DESCRIPTION
            session_manager.save_session(user_id, session)
            return (
                f"✅ Equipo seleccionado: *{equipo.get('nombreequipo')}*\n\n"
                f"Ahora, describe detalladamente la falla que presenta el equipo.\n\n"
                f"Incluye información como:\n"
                f"• ¿Qué está fallando?\n"
                f"• ¿Cuándo comenzó la falla?\n"
                f"• ¿Hay algún síntoma específico?"
            )
        else:
            return (
                f"❌ No encontré un equipo con '{message}'.\n\n"
                f"Por favor, verifica el nombre o código e intenta nuevamente.\n"
                f"Escribe 'equipos' para ver la lista completa."
            )
    
    elif state == ConversationState.AWAITING_DESCRIPTION:
        if len(message) < 10:
            return (
                "⚠️ La descripción es muy corta.\n\n"
                "Por favor, proporciona más detalles sobre la falla para que el técnico pueda entender mejor el problema."
            )
        
        session['data']['descripcion'] = message
        session['state'] = ConversationState.AWAITING_PRIORITY
        session_manager.save_session(user_id, session)
        return (
            "📊 *Prioridad de la Falla*\n\n"
            "¿Qué prioridad tiene esta falla?\n\n"
            "1️⃣ *Baja* - No afecta operaciones críticas\n"
            "2️⃣ *Media* - Afecta operaciones normales\n"
            "3️⃣ *Alta* - Afecta operaciones críticas\n"
            "4️⃣ *Crítica* - Detiene completamente las operaciones\n\n"
            "Responde con: Baja, Media, Alta o Crítica"
        )
    
    elif state == ConversationState.AWAITING_PRIORITY:
        prioridad_map = {
            'baja': 'Baja',
            'media': 'Media',
            'alta': 'Alta',
            'critica': 'Crítica',
            'crítica': 'Crítica',
            '1': 'Baja',
            '2': 'Media',
            '3': 'Alta',
            '4': 'Crítica'
        }
        
        prioridad = prioridad_map.get(message_lower)
        
        if prioridad:
            session['data']['prioridad'] = prioridad
            session['state'] = ConversationState.CONFIRMING_REPORT
            session_manager.save_session(user_id, session)
            
            equipo = session['data']['equipo']
            descripcion = session['data']['descripcion']
            
            return (
                "📝 *Resumen del Reporte*\n\n"
                f"🔧 Equipo: {equipo.get('nombreequipo')}\n"
                f"📝 Descripción: {descripcion}\n"
                f"⚠️ Prioridad: {prioridad}\n\n"
                f"¿Confirmas el reporte? (Sí/No)"
            )
        else:
            return (
                "❌ Prioridad no válida.\n\n"
                "Por favor, responde con: Baja, Media, Alta o Crítica"
            )
    
    elif state == ConversationState.CONFIRMING_REPORT:
        if message_lower in ['si', 'sí', 'yes', 'confirmar', 'ok']:
            equipo = session['data']['equipo']
            descripcion = session['data']['descripcion']
            prioridad = session['data']['prioridad']
            
            resultado, error = create_fault_report(
                equipo['idequipo'],
                descripcion,
                prioridad
            )
            
            reset_user_session(user_id)
            
            if resultado:
                numero_ot = resultado.get('numeroot', 'N/A')
                return (
                    f"✅ *Reporte Creado Exitosamente*\n\n"
                    f"📋 Número de OT: **{numero_ot}**\n"
                    f"🔧 Equipo: {equipo.get('nombreequipo')}\n"
                    f"⚠️ Prioridad: {prioridad}\n\n"
                    f"El técnico será notificado y se asignará la orden de trabajo pronto.\n\n"
                    f"¿Necesitas ayuda con algo más?"
                )
            else:
                return (
                    f"❌ *Error al Crear el Reporte*\n\n"
                    f"{error}\n\n"
                    f"Por favor, intenta nuevamente o contacta al administrador."
                )
        
        elif message_lower in ['no', 'cancelar']:
            reset_user_session(user_id)
            return "❌ Reporte cancelado. ¿En qué más puedo ayudarte?"
        
        else:
            return "Por favor, responde 'Sí' para confirmar o 'No' para cancelar."
    
    elif state == ConversationState.QUERYING_OT:
        ot_match = re.search(r'OT-[\w-]+', message, re.IGNORECASE)
        
        if ot_match:
            numero_ot = ot_match.group(0)
            orden = get_orden_trabajo(numero_ot)
            
            reset_user_session(user_id)
            
            if orden:
                return format_orden_trabajo_info(orden) + "\n\n¿Necesitas consultar otra OT?"
            else:
                return (
                    f"❌ No se encontró la orden de trabajo '{numero_ot}'.\n\n"
                    f"Verifica el número e intenta nuevamente."
                )
        else:
            return (
                "❌ No reconocí el número de OT.\n\n"
                "Por favor, proporciona el número en el formato: OT-XXX-XXX"
            )
    
    else:
        reset_user_session(user_id)
        return "❌ Hubo un error. Por favor, intenta nuevamente."

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', 'unknown')
    
    resp = MessagingResponse()
    msg = resp.message()
    
    response_text = process_message(from_number, incoming_msg)
    msg.body(response_text)
    
    return str(resp)

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    message = data.get('message', '').strip()
    user_id = data.get('user_id', 'web_user')
    
    if not message:
        return jsonify({'error': 'Mensaje vacío'}), 400
    
    response_text = process_message(user_id, message)
    
    return jsonify({
        'response': response_text,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'service': 'Somacor CMMS Bot',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

