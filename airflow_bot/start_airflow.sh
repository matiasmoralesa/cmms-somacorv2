#!/bin/bash
# Script para iniciar Apache Airflow

echo "=========================================="
echo "Iniciando Apache Airflow"
echo "=========================================="
echo ""

# Directorio del proyecto
cd "$(dirname "$0")"

# Activar entorno virtual
source venv_airflow/bin/activate

# Configurar variables de entorno
export AIRFLOW_HOME=/home/ubuntu/cmms-somacorv2/airflow_bot
export AIRFLOW__CORE__DAGS_FOLDER=/home/ubuntu/cmms-somacorv2/airflow_bot/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__EXECUTOR=SequentialExecutor
export AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True
export AIRFLOW__WEBSERVER__SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(16))")

# Cargar variables de entorno desde .env
if [ -f .env ]; then
    echo "✓ Cargando variables de entorno desde .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Crear directorios necesarios
mkdir -p logs
mkdir -p dags

echo ""
echo "Configuración:"
echo "  AIRFLOW_HOME: $AIRFLOW_HOME"
echo "  DAGS_FOLDER: $AIRFLOW__CORE__DAGS_FOLDER"
echo "  EXECUTOR: $AIRFLOW__CORE__EXECUTOR"
echo ""

# Verificar si la base de datos está inicializada
if [ ! -f "$AIRFLOW_HOME/airflow.db" ]; then
    echo "Inicializando base de datos de Airflow..."
    airflow db migrate
    
    echo ""
    echo "Creando usuario administrador..."
    airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@somacor.cl \
        --password admin123
fi

echo ""
echo "=========================================="
echo "Iniciando servicios de Airflow"
echo "=========================================="
echo ""

# Iniciar webserver en segundo plano
echo "Iniciando Airflow Webserver en puerto 8080..."
nohup airflow webserver --port 8080 > logs/webserver.log 2>&1 &
WEBSERVER_PID=$!
echo "  PID: $WEBSERVER_PID"

# Esperar un poco
sleep 3

# Iniciar scheduler en segundo plano
echo "Iniciando Airflow Scheduler..."
nohup airflow scheduler > logs/scheduler.log 2>&1 &
SCHEDULER_PID=$!
echo "  PID: $SCHEDULER_PID"

echo ""
echo "=========================================="
echo "Airflow iniciado correctamente"
echo "=========================================="
echo ""
echo "URLs:"
echo "  Webserver: http://localhost:8080"
echo "  Usuario: admin"
echo "  Password: admin123"
echo ""
echo "Procesos:"
echo "  Webserver PID: $WEBSERVER_PID"
echo "  Scheduler PID: $SCHEDULER_PID"
echo ""
echo "Logs:"
echo "  Webserver: $AIRFLOW_HOME/logs/webserver.log"
echo "  Scheduler: $AIRFLOW_HOME/logs/scheduler.log"
echo ""
echo "Para detener Airflow:"
echo "  ./stop_airflow.sh"
echo ""
echo "Para ver los logs:"
echo "  tail -f logs/webserver.log"
echo "  tail -f logs/scheduler.log"
echo ""

