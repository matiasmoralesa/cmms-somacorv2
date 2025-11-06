"""
### DAG de Consulta de Estado de OT

Este DAG se encarga de consultar el estado de una Orden de Trabajo (OT) específica y
enviar la respuesta a través del nuevo servicio de notificaciones.
"""

from airflow.decorators import dag, task
from pendulum import datetime
import requests
import re

# URL del servicio de notificaciones
NOTIFICATION_URL = "http://localhost:5001/api/notify"

def get_orden_trabajo(numero_ot):
    try:
        response = requests.get(f'http://localhost:8000/api/ordenes-trabajo/', timeout=5)
        if response.status_code == 200:
            ordenes = response.json()
            for orden in ordenes:
                if orden.get('numeroot', '').lower() == numero_ot.lower():
                    return orden
        return None
    except Exception as e:
        print(f"Error al obtener orden de trabajo: {str(e)}")
        return None

def format_orden_trabajo_info(orden):
    if not orden:
        return "No se encontró la orden de trabajo."
    numero = orden.get('numeroot', 'N/A')
    estado = orden.get('estado_nombre', 'N/A')
    equipo = orden.get('equipo_nombre', 'N/A')
    return f"La orden de trabajo {numero} para el equipo {equipo} se encuentra en estado: {estado}."

@dag(
    dag_id='query_ot_status_workflow',
    start_date=datetime(2025, 10, 7),
    schedule=None,
    catchup=False,
    tags=['somacor', 'omnibot'],
)
def query_ot_status_workflow():
    @task
    def extract_ot_number(message: str):
        ot_match = re.search(r'OT-[\w-]+', message, re.IGNORECASE)
        if ot_match:
            return ot_match.group(0)
        return None

    @task
    def query_ot_api(ot_number: str):
        if not ot_number:
            return None
        return get_orden_trabajo(ot_number)

    @task
    def format_ot_response(ot_data: dict):
        return format_orden_trabajo_info(ot_data)

    @task
    def send_notification(user_id: str, message: str, service_name: str = 'telegram'):
        try:
            payload = {
                'service_name': service_name,
                'user_id': user_id,
                'message': message
            }
            requests.post(NOTIFICATION_URL, json=payload)
        except Exception as e:
            print(f"Error al enviar la notificación: {str(e)}")

    ot_number = extract_ot_number(message="{{ dag_run.conf.message }}")
    ot_data = query_ot_api(ot_number=ot_number)
    formatted_message = format_ot_response(ot_data=ot_data)
    send_notification(user_id="{{ dag_run.conf.user_id }}", message=formatted_message)

query_ot_status_workflow_dag = query_ot_status_workflow()

