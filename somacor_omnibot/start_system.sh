#!/bin/bash

# Script de inicio rápido para el sistema completo del bot omnicanal
# Somacor-CMMS

echo "🚀 Iniciando Sistema Bot Omnicanal Somacor-CMMS"
echo "================================================"

# Verificar que estamos en el directorio correcto
if [ ! -f "api_gateway.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio somacor_omnibot"
    exit 1
fi

# Cargar variables de entorno si existe .env
if [ -f ".env" ]; then
    echo "📄 Cargando variables de entorno..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  Archivo .env no encontrado. Creando uno básico..."
    cat > .env << EOF
TELEGRAM_BOT_TOKEN=tu_token_aqui
CMMS_API_BASE_URL=http://localhost:8000/api/
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
API_GATEWAY_URL=http://localhost:5001
EOF
    echo "✏️  Por favor, edita el archivo .env con tus configuraciones reales"
fi

# Función para verificar si un servicio está ejecutándose
check_service() {
    local service_name=$1
    local port=$2
    if nc -z localhost $port 2>/dev/null; then
        echo "✅ $service_name está ejecutándose en puerto $port"
        return 0
    else
        echo "❌ $service_name NO está ejecutándose en puerto $port"
        return 1
    fi
}

# Verificar servicios base
echo ""
echo "🔍 Verificando servicios base..."
check_service "Redis" 6379
check_service "CMMS API" 8000

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    echo "📥 Instalando dependencias..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Entorno virtual encontrado"
    source venv/bin/activate
fi

# Configurar Airflow si no está configurado
if [ ! -d "airflow_home" ]; then
    echo ""
    echo "⚙️  Configurando Airflow por primera vez..."
    ./setup_airflow.sh
else
    echo "✅ Airflow ya está configurado"
fi

# Función para iniciar un servicio en background
start_service() {
    local service_name=$1
    local command=$2
    local log_file=$3
    
    echo "🚀 Iniciando $service_name..."
    nohup $command > $log_file 2>&1 &
    local pid=$!
    echo $pid > "${service_name,,}.pid"
    echo "   PID: $pid, Logs: $log_file"
}

# Crear directorio de logs
mkdir -p logs

echo ""
echo "🚀 Iniciando servicios del bot..."

# Iniciar Airflow Scheduler
start_service "Airflow-Scheduler" "airflow scheduler" "logs/airflow-scheduler.log"

# Esperar un poco para que el scheduler inicie
sleep 3

# Iniciar Airflow Webserver
start_service "Airflow-Webserver" "airflow webserver --port 8080" "logs/airflow-webserver.log"

# Iniciar API Gateway
start_service "API-Gateway" "python api_gateway.py" "logs/api-gateway.log"

# Esperar a que los servicios inicien
echo ""
echo "⏳ Esperando que los servicios inicien..."
sleep 10

# Verificar que los servicios estén ejecutándose
echo ""
echo "🔍 Verificando servicios del bot..."
check_service "Airflow Webserver" 8080
check_service "API Gateway" 5001

echo ""
echo "📊 URLs de acceso:"
echo "   • Airflow UI: http://localhost:8080 (admin/admin123)"
echo "   • API Gateway: http://localhost:5001"
echo "   • CMMS Admin: http://localhost:8000/admin/"

echo ""
echo "📱 Para iniciar el bot de Telegram:"
echo "   python telegram_bot.py"

echo ""
echo "📝 Archivos de logs:"
echo "   • Airflow Scheduler: logs/airflow-scheduler.log"
echo "   • Airflow Webserver: logs/airflow-webserver.log"
echo "   • API Gateway: logs/api-gateway.log"

echo ""
echo "🛑 Para detener todos los servicios:"
echo "   ./stop_system.sh"

echo ""
echo "✅ Sistema iniciado correctamente!"
