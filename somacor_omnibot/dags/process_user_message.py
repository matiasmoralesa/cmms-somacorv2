_user_message.py
"""
### DAG de Procesamiento de Mensajes de Usuario

Este DAG se encarga de recibir los mensajes de los usuarios, analizar la intención y enrutar la conversación al DAG de flujo de trabajo correspondiente.
"""

from airflow.operators.python import BranchPythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.decorators import dag, task
from pendulum import datetime

@dag(
    dag_id='process_user_message',
    start_date=datetime(2025, 10, 7),
    schedule=None,
    catchup=False,
    tags=['somacor', 'omnibot'],
)
def process_user_message():
    @task
    def analyze_intent(message: str, session: dict):
        message_lower = message.lower().strip()
        state = session.get('state', 'idle')

        if state != 'idle':
            return state

        if 'reportar' in message_lower and 'falla' in message_lower:
            return 'reporting_fault'
        elif 'estado' in message_lower or 'consultar' in message_lower:
            return 'querying_ot'
        elif 'equipos' in message_lower or 'listar' in message_lower:
            return 'list_equipments'
        elif 'ayuda' in message_lower or 'help' in message_lower or '?' in message_lower:
            return 'send_help_message'
        elif 'hola' in message_lower or 'buenos' in message_lower or 'buenas' in message_lower:
            return 'send_greeting'
        else:
            return 'unknown'

    @task.branch
    def route_to_workflow(intent: str):
        if intent == 'reporting_fault':
            return 'trigger_report_fault'
        elif intent == 'querying_ot':
            return 'trigger_query_ot'
        elif intent == 'list_equipments':
            return 'trigger_list_equipments'
        elif intent == 'send_help_message':
            return 'send_help_message_task'
        elif intent == 'send_greeting':
            return 'send_greeting_task'
        else:
            return 'send_unknown_message_task'

    @task
    def send_help_message_task(user_id: str):
        # Lógica para enviar mensaje de ayuda
        pass

    @task
    def send_greeting_task(user_id: str):
        # Lógica para enviar saludo
        pass

    @task
    def send_unknown_message_task(user_id: str):
        # Lógica para enviar mensaje de intención no reconocida
        pass

    trigger_report_fault = TriggerDagRunOperator(
        task_id='trigger_report_fault',
        trigger_dag_id='report_fault_workflow',
        conf={ "user_id": "{{ dag_run.conf.user_id }}", "message": "{{ dag_run.conf.message }}" }
    )

    trigger_query_ot = TriggerDagRunOperator(
        task_id='trigger_query_ot',
        trigger_dag_id='query_ot_status_workflow',
        conf={ "user_id": "{{ dag_run.conf.user_id }}", "message": "{{ dag_run.conf.message }}" }
    )

    trigger_list_equipments = TriggerDagRunOperator(
        task_id='trigger_list_equipments',
        trigger_dag_id='list_equipments_workflow',
        conf={ "user_id": "{{ dag_run.conf.user_id }}", "message": "{{ dag_run.conf.message }}" }
    )

    intent = analyze_intent(message="{{ dag_run.conf.message }}", session="{{ dag_run.conf.session }}")
    route = route_to_workflow(intent=intent)

    route >> [trigger_report_fault, trigger_query_ot, trigger_list_equipments, send_help_message_task, send_greeting_task, send_unknown_message_task]

process_user_message_dag = process_user_message()

