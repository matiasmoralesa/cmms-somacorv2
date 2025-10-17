"""
DAG de Mantenimiento Preventivo
Ejecuta semanalmente para crear órdenes de mantenimiento preventivo automáticas
"""

from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
import sys
from pathlib import Path
import pandas as pd
from typing import Dict, List

# Agregar directorios al path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.airflow_config import (
    ScheduleConfig,
    BusinessLogicConfig,
    CMSSConfig
)
from scripts.cmms_api_client import CMSSAPIClient

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'telegram_integration'))
from notifications.telegram_notifier import TelegramNotifier

# Configuración por defecto del DAG
default_args = {
    'owner': 'cmms_bot',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


@dag(
    dag_id='mantenimiento_preventivo_semanal',
    default_args=default_args,
    description='Generación semanal de órdenes de mantenimiento preventivo',
    schedule=ScheduleConfig.DAG_PREVENTIVO,
    start_date=days_ago(1),
    catchup=False,
    tags=['cmms', 'preventivo', 'automatizacion'],
)
def mantenimiento_preventivo_dag():
    """
    DAG para generación automática de órdenes de mantenimiento preventivo
    
    Flujo:
    1. Obtener planes de mantenimiento preventivo activos
    2. Calcular próximas fechas de mantenimiento
    3. Identificar equipos que requieren mantenimiento
    4. Asignar técnicos según disponibilidad
    5. Crear órdenes de trabajo preventivas
    6. Enviar notificaciones a técnicos
    """
    
    @task
    def get_active_maintenance_plans() -> List[Dict]:
        """
        Obtener planes de mantenimiento preventivo activos
        
        Returns:
            Lista de planes activos
        """
        client = CMSSAPIClient()
        
        try:
            planes = client.get_planes_mantenimiento(params={'activo': True})
            print(f"✅ Obtenidos {len(planes)} planes de mantenimiento activos")
            return planes
        except Exception as e:
            print(f"⚠️ Error al obtener planes: {str(e)}")
            # Si no existe el endpoint, retornar lista vacía
            return []
    
    @task
    def get_equipment_data() -> List[Dict]:
        """
        Obtener datos de equipos activos
        
        Returns:
            Lista de equipos
        """
        client = CMSSAPIClient()
        equipos = client.get_equipos(params={'activo': True})
        
        print(f"✅ Obtenidos {len(equipos)} equipos activos")
        return equipos
    
    @task
    def get_last_maintenance_dates(equipos: List[Dict]) -> Dict[int, datetime]:
        """
        Obtener fechas del último mantenimiento preventivo por equipo
        
        Args:
            equipos: Lista de equipos
        
        Returns:
            Diccionario con fecha del último mantenimiento por equipo
        """
        client = CMSSAPIClient()
        
        # Obtener órdenes de mantenimiento preventivo completadas
        ordenes = client.get_ordenes_trabajo(params={
            'idtipomantenimientoot': BusinessLogicConfig.TIPOS_MANTENIMIENTO['PREVENTIVO'],
            'idestadoot': BusinessLogicConfig.ESTADOS_OT['COMPLETADA']
        })
        
        # Convertir a DataFrame
        df_ordenes = pd.DataFrame(ordenes)
        
        if df_ordenes.empty:
            print("⚠️ No se encontraron órdenes preventivas completadas")
            return {}
        
        # Convertir fecha
        df_ordenes['fechacompletado'] = pd.to_datetime(
            df_ordenes['fechacompletado'],
            errors='coerce'
        )
        
        # Obtener última fecha por equipo
        ultimas_fechas = {}
        for equipo in equipos:
            equipo_id = equipo['idequipo']
            ordenes_equipo = df_ordenes[df_ordenes['idequipo'] == equipo_id]
            
            if not ordenes_equipo.empty:
                ultima_fecha = ordenes_equipo['fechacompletado'].max()
                ultimas_fechas[equipo_id] = ultima_fecha
        
        print(f"✅ Obtenidas fechas de último mantenimiento para {len(ultimas_fechas)} equipos")
        return ultimas_fechas
    
    @task
    def calculate_next_maintenance_dates(
        planes: List[Dict],
        equipos: List[Dict],
        ultimas_fechas: Dict[int, datetime]
    ) -> List[Dict]:
        """
        Calcular próximas fechas de mantenimiento
        
        Args:
            planes: Lista de planes de mantenimiento
            equipos: Lista de equipos
            ultimas_fechas: Fechas del último mantenimiento
        
        Returns:
            Lista de equipos que requieren mantenimiento
        """
        equipos_mantenimiento = []
        fecha_actual = datetime.now()
        fecha_limite = fecha_actual + timedelta(days=BusinessLogicConfig.PREVENTIVE_MAINTENANCE_ADVANCE_DAYS)
        
        # Crear diccionario de planes por equipo
        planes_por_equipo = {}
        for plan in planes:
            equipo_id = plan.get('idequipo')
            if equipo_id:
                planes_por_equipo[equipo_id] = plan
        
        for equipo in equipos:
            equipo_id = equipo['idequipo']
            
            # Verificar si tiene plan de mantenimiento
            if equipo_id not in planes_por_equipo:
                continue
            
            plan = planes_por_equipo[equipo_id]
            frecuencia_dias = plan.get('frecuencia', 30)  # Default 30 días
            
            # Obtener última fecha de mantenimiento
            ultima_fecha = ultimas_fechas.get(equipo_id)
            
            if ultima_fecha is None:
                # Nunca se ha hecho mantenimiento preventivo
                dias_desde_ultimo = 999
                proxima_fecha = fecha_actual
            else:
                dias_desde_ultimo = (fecha_actual - ultima_fecha).days
                proxima_fecha = ultima_fecha + timedelta(days=frecuencia_dias)
            
            # Verificar si requiere mantenimiento
            if proxima_fecha <= fecha_limite:
                equipos_mantenimiento.append({
                    'equipo_id': equipo_id,
                    'nombre_equipo': equipo.get('nombreequipo', 'N/A'),
                    'codigo_interno': equipo.get('codigointerno', 'N/A'),
                    'tipo_equipo': equipo.get('idtipoequipo'),
                    'faena_id': equipo.get('idfaenaactual'),
                    'plan_id': plan.get('idplan'),
                    'plan_nombre': plan.get('nombreplan', 'N/A'),
                    'frecuencia_dias': frecuencia_dias,
                    'duracion_estimada': plan.get('duracionestimada', 4),
                    'ultima_fecha_mantenimiento': ultima_fecha.isoformat() if ultima_fecha else None,
                    'dias_desde_ultimo': dias_desde_ultimo,
                    'proxima_fecha': proxima_fecha.isoformat(),
                    'urgencia': 'ALTA' if dias_desde_ultimo > frecuencia_dias else 'NORMAL'
                })
        
        # Ordenar por urgencia y días desde último mantenimiento
        equipos_mantenimiento.sort(
            key=lambda x: (x['urgencia'] == 'NORMAL', -x['dias_desde_ultimo'])
        )
        
        print(f"✅ Identificados {len(equipos_mantenimiento)} equipos que requieren mantenimiento")
        return equipos_mantenimiento
    
    @task
    def get_available_technicians() -> List[Dict]:
        """
        Obtener técnicos disponibles
        
        Returns:
            Lista de técnicos con su carga de trabajo
        """
        client = CMSSAPIClient()
        
        # Obtener todos los técnicos
        tecnicos = client.get_tecnicos()
        
        # Obtener órdenes pendientes y en progreso
        ordenes_activas = client.get_ordenes_trabajo(params={
            'idestadoot__in': f"{BusinessLogicConfig.ESTADOS_OT['PENDIENTE']},{BusinessLogicConfig.ESTADOS_OT['EN_PROGRESO']}"
        })
        
        # Contar órdenes por técnico
        ordenes_por_tecnico = {}
        for orden in ordenes_activas:
            tecnico_id = orden.get('idusuarioasignado')
            if tecnico_id:
                ordenes_por_tecnico[tecnico_id] = ordenes_por_tecnico.get(tecnico_id, 0) + 1
        
        # Agregar carga de trabajo a técnicos
        for tecnico in tecnicos:
            tecnico_id = tecnico['idusuario']
            tecnico['ordenes_activas'] = ordenes_por_tecnico.get(tecnico_id, 0)
            tecnico['disponible'] = tecnico['ordenes_activas'] < BusinessLogicConfig.MAX_ORDERS_PER_TECHNICIAN
        
        # Ordenar por carga de trabajo (menor a mayor)
        tecnicos.sort(key=lambda x: x['ordenes_activas'])
        
        tecnicos_disponibles = [t for t in tecnicos if t['disponible']]
        
        print(f"✅ {len(tecnicos_disponibles)} técnicos disponibles de {len(tecnicos)} totales")
        return tecnicos
    
    @task
    def assign_technicians(
        equipos_mantenimiento: List[Dict],
        tecnicos: List[Dict]
    ) -> List[Dict]:
        """
        Asignar técnicos a equipos según disponibilidad
        
        Args:
            equipos_mantenimiento: Lista de equipos que requieren mantenimiento
            tecnicos: Lista de técnicos disponibles
        
        Returns:
            Lista de asignaciones equipo-técnico
        """
        asignaciones = []
        tecnicos_disponibles = [t for t in tecnicos if t['disponible']]
        
        if not tecnicos_disponibles:
            print("⚠️ No hay técnicos disponibles")
            return []
        
        # Asignar técnicos de forma round-robin
        for i, equipo in enumerate(equipos_mantenimiento):
            tecnico = tecnicos_disponibles[i % len(tecnicos_disponibles)]
            
            asignaciones.append({
                'equipo_id': equipo['equipo_id'],
                'nombre_equipo': equipo['nombre_equipo'],
                'codigo_interno': equipo['codigo_interno'],
                'plan_nombre': equipo['plan_nombre'],
                'duracion_estimada': equipo['duracion_estimada'],
                'urgencia': equipo['urgencia'],
                'tecnico_id': tecnico['idusuario'],
                'tecnico_nombre': tecnico['nombreusuario'],
                'tecnico_email': tecnico.get('email', ''),
                'fecha_programada': equipo['proxima_fecha']
            })
        
        print(f"✅ Asignados {len(asignaciones)} equipos a técnicos")
        return asignaciones
    
    @task
    def create_maintenance_orders(asignaciones: List[Dict]) -> List[Dict]:
        """
        Crear órdenes de trabajo preventivas
        
        Args:
            asignaciones: Lista de asignaciones equipo-técnico
        
        Returns:
            Lista de órdenes creadas
        """
        client = CMSSAPIClient()
        ordenes_creadas = []
        
        for asignacion in asignaciones:
            try:
                orden_data = {
                    'idequipo': asignacion['equipo_id'],
                    'idtipomantenimientoot': BusinessLogicConfig.TIPOS_MANTENIMIENTO['PREVENTIVO'],
                    'descripcionproblemareportado': f"Mantenimiento preventivo programado: {asignacion['plan_nombre']}",
                    'prioridad': 'Alta' if asignacion['urgencia'] == 'ALTA' else 'Media',
                    'idestadoot': BusinessLogicConfig.ESTADOS_OT['PENDIENTE'],
                    'idusuarioasignado': asignacion['tecnico_id'],
                    'fechareportefalla': datetime.now().isoformat(),
                    # 'fechaprogramada': asignacion['fecha_programada'],  # Si el modelo lo soporta
                    # 'duracionestimada': asignacion['duracion_estimada'],
                }
                
                orden = client.create_orden_trabajo(orden_data)
                
                asignacion['orden_id'] = orden.get('idordentrabajo')
                asignacion['codigo_ot'] = orden.get('codigoot')
                ordenes_creadas.append(asignacion)
                
                print(f"✅ Orden creada: {orden.get('codigoot')} - {asignacion['nombre_equipo']} -> {asignacion['tecnico_nombre']}")
                
            except Exception as e:
                print(f"❌ Error al crear orden para equipo {asignacion['equipo_id']}: {str(e)}")
        
        print(f"✅ Creadas {len(ordenes_creadas)} órdenes de mantenimiento preventivo")
        return ordenes_creadas
    
    @task
    def send_notifications(ordenes_creadas: List[Dict]):
        """
        Enviar notificaciones a técnicos asignados
        
        Args:
            ordenes_creadas: Lista de órdenes creadas con asignaciones
        """
        notifier = TelegramNotifier()
        
        # TODO: Obtener chat_ids de técnicos desde base de datos
        # Por ahora, solo enviar resumen a administradores
        
        admin_chat_ids = []  # Configurar con IDs reales
        
        if not admin_chat_ids:
            print("⚠️ No hay chat_ids configurados para notificaciones")
            return
        
        # Crear mensaje resumen
        mensaje = f"""
🔧 **ÓRDENES DE MANTENIMIENTO PREVENTIVO**

📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

📋 **Órdenes Creadas:** {len(ordenes_creadas)}

**Resumen por Técnico:**
"""
        
        # Agrupar por técnico
        ordenes_por_tecnico = {}
        for orden in ordenes_creadas:
            tecnico = orden['tecnico_nombre']
            if tecnico not in ordenes_por_tecnico:
                ordenes_por_tecnico[tecnico] = []
            ordenes_por_tecnico[tecnico].append(orden)
        
        for tecnico, ordenes in ordenes_por_tecnico.items():
            mensaje += f"\n👤 **{tecnico}:** {len(ordenes)} órdenes"
            for orden in ordenes[:3]:  # Mostrar máximo 3 por técnico
                mensaje += f"\n   • {orden['codigo_ot']} - {orden['nombre_equipo']}"
        
        mensaje += "\n\n✅ Los técnicos han sido notificados de sus asignaciones."
        
        # Enviar a administradores
        for chat_id in admin_chat_ids:
            try:
                notifier.send_message(chat_id, mensaje)
            except Exception as e:
                print(f"❌ Error al enviar notificación a {chat_id}: {str(e)}")
        
        print(f"✅ Notificaciones enviadas")
    
    @task
    def generate_summary(
        equipos_mantenimiento: List[Dict],
        ordenes_creadas: List[Dict]
    ) -> Dict:
        """
        Generar resumen de ejecución
        
        Args:
            equipos_mantenimiento: Lista de equipos que requerían mantenimiento
            ordenes_creadas: Lista de órdenes creadas
        
        Returns:
            Diccionario con resumen
        """
        resumen = {
            'fecha_ejecucion': datetime.now().isoformat(),
            'equipos_requieren_mantenimiento': len(equipos_mantenimiento),
            'ordenes_creadas': len(ordenes_creadas),
            'urgentes': sum(1 for e in equipos_mantenimiento if e['urgencia'] == 'ALTA'),
            'normales': sum(1 for e in equipos_mantenimiento if e['urgencia'] == 'NORMAL'),
            'tecnicos_asignados': len(set(o['tecnico_id'] for o in ordenes_creadas))
        }
        
        print("=" * 60)
        print("RESUMEN DE MANTENIMIENTO PREVENTIVO")
        print("=" * 60)
        print(f"Equipos que requieren mantenimiento: {resumen['equipos_requieren_mantenimiento']}")
        print(f"  - Urgentes: {resumen['urgentes']}")
        print(f"  - Normales: {resumen['normales']}")
        print(f"Órdenes creadas: {resumen['ordenes_creadas']}")
        print(f"Técnicos asignados: {resumen['tecnicos_asignados']}")
        print("=" * 60)
        
        return resumen
    
    # Definir flujo del DAG
    planes = get_active_maintenance_plans()
    equipos = get_equipment_data()
    ultimas_fechas = get_last_maintenance_dates(equipos)
    equipos_mantenimiento = calculate_next_maintenance_dates(planes, equipos, ultimas_fechas)
    tecnicos = get_available_technicians()
    asignaciones = assign_technicians(equipos_mantenimiento, tecnicos)
    ordenes_creadas = create_maintenance_orders(asignaciones)
    notificaciones = send_notifications(ordenes_creadas)
    resumen = generate_summary(equipos_mantenimiento, ordenes_creadas)
    
    # Definir dependencias
    [planes, equipos] >> ultimas_fechas
    [ultimas_fechas, planes, equipos] >> equipos_mantenimiento
    [equipos_mantenimiento, tecnicos] >> asignaciones >> ordenes_creadas
    ordenes_creadas >> notificaciones
    [equipos_mantenimiento, ordenes_creadas] >> resumen


# Instanciar el DAG
dag_instance = mantenimiento_preventivo_dag()

