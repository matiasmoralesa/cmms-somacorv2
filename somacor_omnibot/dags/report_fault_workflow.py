"""
### DAG de Flujo de Reporte de Fallas

Este DAG gestiona el flujo conversacional para que un usuario reporte una falla en un equipo.
"""

from airflow.decorators import dag, task
from pendulum import datetime

@dag(
    dag_id='report_fault_workflow',
    start_date=datetime(2025, 10, 7),
    schedule=None,
    catchup=False,
    tags=['somacor', 'omnibot'],
)
def report_fault_workflow():
    @task
    def get_fault_session(user_id: str):
        # Lógica para obtener la sesión de Redis
        pass

    @task.branch
    def determine_step(session: dict):
        state = session.get('state', 'idle')
        if state == 'awaiting_equipment':
            return 'request_equipment_task'
        elif state == 'awaiting_description':
            return 'validate_equipment_task'
        # ... y así sucesivamente para cada paso

    # Tareas para cada paso de la conversación
    @task
    def request_equipment_task(user_id: str):
        pass

    @task
    def validate_equipment_task(user_id: str, message: str):
        pass

    # ... más tareas

    session = get_fault_session(user_id="{{ dag_run.conf.user_id }}")
    step = determine_step(session=session)

    step >> [request_equipment_task, validate_equipment_task]

report_fault_workflow_dag = report_fault_workflow()

