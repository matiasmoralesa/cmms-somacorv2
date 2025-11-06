"""
Configuración centralizada para Apache Airflow
Bot Asistente CMMS Somacor v2
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class AirflowConfig:
    """Configuración de Apache Airflow"""
    
    # Directorios
    AIRFLOW_HOME = os.getenv('AIRFLOW_HOME', '/home/ubuntu/cmms-somacorv2/airflow_bot')
    DAGS_FOLDER = os.getenv('AIRFLOW__CORE__DAGS_FOLDER', f'{AIRFLOW_HOME}/dags')
    PLUGINS_FOLDER = f'{AIRFLOW_HOME}/plugins'
    LOGS_FOLDER = f'{AIRFLOW_HOME}/logs'
    
    # Executor
    EXECUTOR = os.getenv('AIRFLOW__CORE__EXECUTOR', 'LocalExecutor')
    
    # Database
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
    
    if DATABASE_TYPE == 'postgresql':
        DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
        DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')
        DATABASE_NAME = os.getenv('DATABASE_NAME', 'cmms_somacor')
        DATABASE_USER = os.getenv('DATABASE_USER', 'cmms_user')
        DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', '')
        SQL_ALCHEMY_CONN = f'postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
    else:
        DATABASE_PATH = os.getenv('DATABASE_PATH', f'{AIRFLOW_HOME}/airflow.db')
        SQL_ALCHEMY_CONN = f'sqlite:///{DATABASE_PATH}'
    
    # Webserver
    WEBSERVER_PORT = 8080
    SECRET_KEY = os.getenv('AIRFLOW__WEBSERVER__SECRET_KEY', 'temporary_secret_key_change_in_production')
    
    # Scheduler
    SCHEDULER_HEARTBEAT_SEC = 5
    
    # DAG Settings
    LOAD_EXAMPLES = os.getenv('AIRFLOW__CORE__LOAD_EXAMPLES', 'False').lower() == 'true'
    DEFAULT_TIMEZONE = 'America/Santiago'
    
    # Parallelism
    PARALLELISM = 32
    DAG_CONCURRENCY = 16
    MAX_ACTIVE_RUNS_PER_DAG = 16


class CMSSConfig:
    """Configuración de la API del CMMS"""
    
    API_BASE_URL = os.getenv('CMMS_API_BASE_URL', 'http://localhost:8000/api/v2')
    API_TOKEN = os.getenv('CMMS_API_TOKEN', '')
    API_TIMEOUT = 30
    
    # Endpoints
    EQUIPOS_ENDPOINT = f'{API_BASE_URL}/equipos/'
    ORDENES_TRABAJO_ENDPOINT = f'{API_BASE_URL}/ordenes-trabajo/'
    FAENAS_ENDPOINT = f'{API_BASE_URL}/faenas/'
    USUARIOS_ENDPOINT = f'{API_BASE_URL}/usuarios/'
    TIPOS_EQUIPO_ENDPOINT = f'{API_BASE_URL}/tipos-equipo/'
    CHECKLIST_TEMPLATES_ENDPOINT = f'{API_BASE_URL}/checklist-templates/'
    CHECKLIST_INSTANCE_ENDPOINT = f'{API_BASE_URL}/checklist-instance/'
    DASHBOARD_STATS_ENDPOINT = f'{API_BASE_URL}/dashboard/stats/'
    DASHBOARD_MONTHLY_ENDPOINT = f'{API_BASE_URL}/dashboard/monthly_data/'
    DASHBOARD_MAINTENANCE_TYPES_ENDPOINT = f'{API_BASE_URL}/dashboard/maintenance_types/'


class DaskConfig:
    """Configuración de Dask Cluster"""
    
    SCHEDULER_ADDRESS = os.getenv('DASK_SCHEDULER_ADDRESS', 'tcp://localhost:8786')
    N_WORKERS = int(os.getenv('DASK_N_WORKERS', '4'))
    THREADS_PER_WORKER = int(os.getenv('DASK_THREADS_PER_WORKER', '2'))
    MEMORY_LIMIT = os.getenv('DASK_MEMORY_LIMIT', '4GB')
    
    # Dashboard
    DASHBOARD_ADDRESS = ':8787'


class TelegramConfig:
    """Configuración del Bot de Telegram"""
    
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    ENABLE_NOTIFICATIONS = os.getenv('ENABLE_TELEGRAM_NOTIFICATIONS', 'True').lower() == 'true'
    
    # Comandos
    COMMANDS = {
        'start': 'Iniciar el bot',
        'help': 'Mostrar ayuda',
        'status': 'Ver estado del sistema',
        'equipos': 'Listar equipos',
        'ordenes': 'Listar órdenes de trabajo',
        'alertas': 'Ver alertas activas',
        'reportes': 'Generar reporte',
    }


class RedisConfig:
    """Configuración de Redis"""
    
    HOST = os.getenv('REDIS_HOST', 'localhost')
    PORT = int(os.getenv('REDIS_PORT', '6379'))
    DB = int(os.getenv('REDIS_DB', '0'))
    PASSWORD = os.getenv('REDIS_PASSWORD', '')
    
    # Configuración de conexión
    DECODE_RESPONSES = True
    SOCKET_TIMEOUT = 5
    SOCKET_CONNECT_TIMEOUT = 5


class EmailConfig:
    """Configuración de Email"""
    
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
    FROM_EMAIL = os.getenv('EMAIL_FROM', 'noreply@somacor.com')
    TO_ADMIN = os.getenv('EMAIL_TO_ADMIN', 'admin@somacor.com')
    ENABLE_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'True').lower() == 'true'


class MLConfig:
    """Configuración de Machine Learning"""
    
    MODELS_PATH = os.getenv('ML_MODELS_PATH', '/home/ubuntu/cmms-somacorv2/ml_models/models')
    RETRAIN_INTERVAL_DAYS = int(os.getenv('ML_RETRAIN_INTERVAL_DAYS', '30'))
    MIN_TRAINING_SAMPLES = int(os.getenv('ML_MIN_TRAINING_SAMPLES', '100'))
    
    # Modelos
    FAILURE_PREDICTION_MODEL = f'{MODELS_PATH}/failure_prediction_model.pkl'
    PRIORITY_CLASSIFICATION_MODEL = f'{MODELS_PATH}/priority_classification_model.pkl'
    TECHNICIAN_ASSIGNMENT_MODEL = f'{MODELS_PATH}/technician_assignment_model.pkl'
    
    # Hiperparámetros
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    CV_FOLDS = 5


class BusinessLogicConfig:
    """Configuración de lógica de negocio"""
    
    # Umbrales de alertas
    MTBF_THRESHOLD_DAYS = int(os.getenv('MTBF_THRESHOLD_DAYS', '30'))
    MTTR_THRESHOLD_HOURS = int(os.getenv('MTTR_THRESHOLD_HOURS', '8'))
    FAILURE_PROBABILITY_THRESHOLD = float(os.getenv('FAILURE_PROBABILITY_THRESHOLD', '0.7'))
    
    # Prioridades
    PRIORITY_URGENT_THRESHOLD = float(os.getenv('PRIORITY_URGENT_THRESHOLD', '0.9'))
    PRIORITY_HIGH_THRESHOLD = float(os.getenv('PRIORITY_HIGH_THRESHOLD', '0.7'))
    PRIORITY_MEDIUM_THRESHOLD = float(os.getenv('PRIORITY_MEDIUM_THRESHOLD', '0.4'))
    
    # Mantenimiento preventivo
    PREVENTIVE_MAINTENANCE_ADVANCE_DAYS = int(os.getenv('PREVENTIVE_MAINTENANCE_ADVANCE_DAYS', '7'))
    MAX_ORDERS_PER_TECHNICIAN = int(os.getenv('MAX_ORDERS_PER_TECHNICIAN', '5'))
    
    # Estados de órdenes de trabajo
    ESTADOS_OT = {
        'PENDIENTE': 1,
        'EN_PROGRESO': 2,
        'COMPLETADA': 3,
        'CANCELADA': 4,
        'EN_ESPERA_REPUESTOS': 5,
    }
    
    # Tipos de mantenimiento
    TIPOS_MANTENIMIENTO = {
        'CORRECTIVO': 1,
        'MODIFICATIVO': 2,
        'PREVENTIVO': 3,
        'INSPECCION': 4,
        'PREDICTIVO': 5,
    }


class LoggingConfig:
    """Configuración de logging"""
    
    LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/home/ubuntu/cmms-somacorv2/airflow_bot/logs/bot_asistente.log')
    
    # Formato
    FORMAT = '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
    
    # Rotación
    ROTATION = '10 MB'
    RETENTION = '30 days'


class ScheduleConfig:
    """Configuración de schedules de DAGs"""
    
    # Formato cron: minuto hora dia mes dia_semana
    DAG_PREDICTIVO = os.getenv('DAG_PREDICTIVO_SCHEDULE', '0 2 * * *')  # Diario a las 2 AM
    DAG_PREVENTIVO = os.getenv('DAG_PREVENTIVO_SCHEDULE', '0 3 * * 1')  # Lunes a las 3 AM
    DAG_CHECKLISTS = os.getenv('DAG_CHECKLISTS_SCHEDULE', '0 1 * * *')  # Diario a la 1 AM
    DAG_REPORTES = os.getenv('DAG_REPORTES_SCHEDULE', '0 4 * * 1')     # Lunes a las 4 AM
    DAG_OPTIMIZACION = os.getenv('DAG_OPTIMIZACION_SCHEDULE', '0 0 * * *')  # Diario a medianoche


# Exportar todas las configuraciones
__all__ = [
    'AirflowConfig',
    'CMSSConfig',
    'DaskConfig',
    'TelegramConfig',
    'RedisConfig',
    'EmailConfig',
    'MLConfig',
    'BusinessLogicConfig',
    'LoggingConfig',
    'ScheduleConfig',
]

