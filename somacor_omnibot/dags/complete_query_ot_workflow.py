"""
### DAG Completo de Consulta de Estado de OT

Este DAG demuestra un flujo completo de consulta de OT con todas las tareas
y dependencias claramente definidas para visualización en Airflow UI.
"""

from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from pendulum import datetime
import requests
import re

# Configuración
CMMS_API_BASE_URL = "http://localhost:8000/api/"
NOTIFICATION_URL = "http://localhost:5001/api/notify"

def extract_ot_number_func(**context):
    """Extrae el número de OT del mensaje del usuario"""
    message = context['dag_run'].conf.get('message', '')
    ot_match = re.search(r'OT-[\w-]+', message, re.IGNORECASE)
    if ot_match:
        return ot_match.group(0)
    return None

def query_cmms_api_func(**context):
    """Consulta la API del CMMS para obtener información de la OT"""
    ot_number = context['task_instance'].xcom_pull(task_ids='extract_ot_number')
    
    if not ot_number:
        return None
    
    try:
        response = requests.get(f'{CMMS_API_BASE_URL}ordenes-trabajo/', timeout=5)
        if response.status_code == 200:
            ordenes = response.json()
            for orden in ordenes:
                if orden.get('numeroot', '').lower() == ot_number.lower():
                    return orden
        return None
    except Exception as e:
        print(f"Error al consultar CMMS API: {str(e)}")
        return None

def format_response_func(**context):
    """Formatea la respuesta para el usuario"""
    ot_data = context['task_instance'].xcom_pull(task_ids='query_cmms_api')
    
    if not ot_data:
        return "❌ No se encontró la orden de trabajo solicitada."
    
    numero = ot_data.get('numeroot', 'N/A')
    estado = ot_data.get('estado_nombre', 'N/A')
    equipo = ot_data.get('equipo_nombre', 'N/A')
    prioridad = ot_data.get('prioridad', 'N/A')
    fecha_emision = ot_data.get('fechaemision', 'N/A')
    
    mensaje = f"📋 *Orden de Trabajo: {numero}*\n\n"
    mensaje += f"🔧 Equipo: {equipo}\n"
    mensaje += f"📊 Estado: {estado}\n"
    mensaje += f"⚠️ Prioridad: {prioridad}\n"
    mensaje += f"📅 Fecha Emisión: {fecha_emision}\n"
    
    return mensaje

def send_notification_func(**context):
    """Envía la notificación al usuario"""
    user_id = context['dag_run'].conf.get('user_id')
    message = context['task_instance'].xcom_pull(task_ids='format_response')
    service_name = context['dag_run'].conf.get('service_name', 'telegram')
    
    try:
        payload = {
            'service_name': service_name,
            'user_id': user_id,
            'message': message
        }
        response = requests.post(NOTIFICATION_URL, json=payload)
        if response.status_code == 200:
            print(f"Notificación enviada exitosamente a {user_id}")
        else:
            print(f"Error al enviar notificación: {response.text}")
    except Exception as e:
        print(f"Error al enviar notificación: {str(e)}")

@dag(
    dag_id='complete_query_ot_workflow',
    start_date=datetime(2025, 10, 7),
    schedule=None,
    catchup=False,
    tags=['somacor', 'omnibot', 'demo'],
    description='Flujo completo de consulta de OT con notificaciones',
)
def complete_query_ot_workflow():
    
    # Tarea inicial
    start_task = DummyOperator(
        task_id='start_workflow',
        doc_md="Inicio del flujo de consulta de OT"
    )
    
    # Extraer número de OT del mensaje
    extract_ot_number = PythonOperator(
        task_id='extract_ot_number',
        python_callable=extract_ot_number_func,
        doc_md="Extrae el número de OT del mensaje del usuario usando regex"
    )
    
    # Validar que se encontró un número de OT
    validate_ot_number = DummyOperator(
        task_id='validate_ot_number',
        doc_md="Valida que se haya extraído un número de OT válido"
    )
    
    # Consultar API del CMMS
    query_cmms_api = PythonOperator(
        task_id='query_cmms_api',
        python_callable=query_cmms_api_func,
        doc_md="Consulta la API del CMMS para obtener información de la OT"
    )
    
    # Procesar respuesta de la API
    process_api_response = DummyOperator(
        task_id='process_api_response',
        doc_md="Procesa la respuesta de la API del CMMS"
    )
    
    # Formatear respuesta para el usuario
    format_response = PythonOperator(
        task_id='format_response',
        python_callable=format_response_func,
        doc_md="Formatea la información de la OT para presentarla al usuario"
    )
    
    # Preparar notificación
    prepare_notification = DummyOperator(
        task_id='prepare_notification',
        doc_md="Prepara los datos para enviar la notificación"
    )
    
    # Enviar notificación
    send_notification = PythonOperator(
        task_id='send_notification',
        python_callable=send_notification_func,
        doc_md="Envía la notificación al usuario a través del servicio configurado"
    )
    
    # Tarea final
    end_task = DummyOperator(
        task_id='end_workflow',
        doc_md="Fin del flujo de consulta de OT"
    )
    
    # Definir dependencias del flujo
    start_task >> extract_ot_number >> validate_ot_number >> query_cmms_api
    query_cmms_api >> process_api_response >> format_response >> prepare_notification
    prepare_notification >> send_notification >> end_task

# Instanciar el DAG
complete_query_ot_workflow_dag = complete_query_ot_workflow()
