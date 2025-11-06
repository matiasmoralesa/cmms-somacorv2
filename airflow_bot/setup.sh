#!/bin/bash

# Script de instalación y configuración del Bot Asistente CMMS
# Sistema con Apache Airflow, Dask y Telegram

set -e  # Salir si hay errores

echo "=========================================="
echo "Bot Asistente CMMS Somacor v2"
echo "Instalación y Configuración"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directorio base
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$BASE_DIR")"

echo -e "${GREEN}Directorio del proyecto: $PROJECT_ROOT${NC}"
echo ""

# Verificar Python
echo "Verificando Python..."
if ! command -v python3.11 &> /dev/null; then
    echo -e "${RED}Python 3.11 no encontrado${NC}"
    echo "Por favor instala Python 3.11 o superior"
    exit 1
fi

PYTHON_VERSION=$(python3.11 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
echo ""

# Crear entorno virtual
echo "Creando entorno virtual..."
if [ ! -d "$BASE_DIR/venv" ]; then
    python3.11 -m venv "$BASE_DIR/venv"
    echo -e "${GREEN}✓ Entorno virtual creado${NC}"
else
    echo -e "${YELLOW}✓ Entorno virtual ya existe${NC}"
fi
echo ""

# Activar entorno virtual
echo "Activando entorno virtual..."
source "$BASE_DIR/venv/bin/activate"
echo -e "${GREEN}✓ Entorno virtual activado${NC}"
echo ""

# Actualizar pip
echo "Actualizando pip..."
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ pip actualizado${NC}"
echo ""

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r "$BASE_DIR/requirements.txt"
echo -e "${GREEN}✓ Dependencias instaladas${NC}"
echo ""

# Crear archivo .env si no existe
echo "Configurando variables de entorno..."
if [ ! -f "$BASE_DIR/.env" ]; then
    cp "$BASE_DIR/.env.example" "$BASE_DIR/.env"
    echo -e "${YELLOW}✓ Archivo .env creado desde .env.example${NC}"
    echo -e "${YELLOW}  Por favor edita $BASE_DIR/.env con tus configuraciones${NC}"
else
    echo -e "${GREEN}✓ Archivo .env ya existe${NC}"
fi
echo ""

# Crear directorios necesarios
echo "Creando directorios..."
mkdir -p "$BASE_DIR/logs"
mkdir -p "$BASE_DIR/dags"
mkdir -p "$BASE_DIR/plugins"
mkdir -p "$PROJECT_ROOT/ml_models/models"
mkdir -p "$PROJECT_ROOT/ml_models/datasets"
echo -e "${GREEN}✓ Directorios creados${NC}"
echo ""

# Inicializar Airflow
echo "Inicializando Apache Airflow..."
export AIRFLOW_HOME="$BASE_DIR"
export AIRFLOW__CORE__DAGS_FOLDER="$BASE_DIR/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# Inicializar base de datos de Airflow
if [ ! -f "$BASE_DIR/airflow.db" ]; then
    airflow db init
    echo -e "${GREEN}✓ Base de datos de Airflow inicializada${NC}"
else
    echo -e "${YELLOW}✓ Base de datos de Airflow ya existe${NC}"
fi
echo ""

# Crear usuario admin de Airflow
echo "Creando usuario admin de Airflow..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@somacor.com \
    --password admin123 2>/dev/null || echo -e "${YELLOW}✓ Usuario admin ya existe${NC}"
echo -e "${GREEN}✓ Usuario admin configurado${NC}"
echo "   Username: admin"
echo "   Password: admin123"
echo ""

# Verificar instalación de Redis
echo "Verificando Redis..."
if command -v redis-cli &> /dev/null; then
    echo -e "${GREEN}✓ Redis instalado${NC}"
    # Verificar si Redis está corriendo
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓ Redis está corriendo${NC}"
    else
        echo -e "${YELLOW}⚠ Redis no está corriendo${NC}"
        echo "  Inicia Redis con: redis-server"
    fi
else
    echo -e "${YELLOW}⚠ Redis no instalado${NC}"
    echo "  Para instalar Redis:"
    echo "    Ubuntu/Debian: sudo apt-get install redis-server"
    echo "    macOS: brew install redis"
fi
echo ""

# Crear scripts de inicio
echo "Creando scripts de inicio..."

# Script para iniciar Airflow
cat > "$BASE_DIR/start_airflow.sh" << 'EOF'
#!/bin/bash
export AIRFLOW_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export AIRFLOW__CORE__DAGS_FOLDER="$AIRFLOW_HOME/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

source "$AIRFLOW_HOME/venv/bin/activate"

echo "Iniciando Airflow Webserver..."
airflow webserver --port 8080 &

echo "Iniciando Airflow Scheduler..."
airflow scheduler &

echo "Airflow iniciado"
echo "Webserver: http://localhost:8080"
echo "Username: admin"
echo "Password: admin123"
EOF

chmod +x "$BASE_DIR/start_airflow.sh"

# Script para detener Airflow
cat > "$BASE_DIR/stop_airflow.sh" << 'EOF'
#!/bin/bash
echo "Deteniendo Airflow..."
pkill -f "airflow webserver"
pkill -f "airflow scheduler"
echo "Airflow detenido"
EOF

chmod +x "$BASE_DIR/stop_airflow.sh"

# Script para iniciar Dask
cat > "$PROJECT_ROOT/dask_cluster/start_dask.sh" << 'EOF'
#!/bin/bash
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$BASE_DIR/../airflow_bot/venv"

source "$VENV_DIR/bin/activate"

echo "Iniciando Dask Scheduler..."
dask-scheduler &

sleep 2

echo "Iniciando Dask Workers..."
dask-worker tcp://localhost:8786 --nworkers 4 --nthreads 2 &

echo "Dask Cluster iniciado"
echo "Scheduler: tcp://localhost:8786"
echo "Dashboard: http://localhost:8787"
EOF

chmod +x "$PROJECT_ROOT/dask_cluster/start_dask.sh"

# Script para detener Dask
cat > "$PROJECT_ROOT/dask_cluster/stop_dask.sh" << 'EOF'
#!/bin/bash
echo "Deteniendo Dask..."
pkill -f "dask-scheduler"
pkill -f "dask-worker"
echo "Dask detenido"
EOF

chmod +x "$PROJECT_ROOT/dask_cluster/stop_dask.sh"

# Script para iniciar bot de Telegram
cat > "$PROJECT_ROOT/telegram_integration/start_bot.sh" << 'EOF'
#!/bin/bash
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$BASE_DIR/../airflow_bot/venv"

source "$VENV_DIR/bin/activate"

echo "Iniciando Bot de Telegram..."
python "$BASE_DIR/bot.py"
EOF

chmod +x "$PROJECT_ROOT/telegram_integration/start_bot.sh"

echo -e "${GREEN}✓ Scripts de inicio creados${NC}"
echo ""

# Crear script maestro de inicio
cat > "$PROJECT_ROOT/start_bot_system.sh" << 'EOF'
#!/bin/bash

echo "=========================================="
echo "Iniciando Sistema Bot Asistente CMMS"
echo "=========================================="
echo ""

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Iniciar Dask
echo "1. Iniciando Dask Cluster..."
"$BASE_DIR/dask_cluster/start_dask.sh"
sleep 3

# Iniciar Airflow
echo ""
echo "2. Iniciando Apache Airflow..."
"$BASE_DIR/airflow_bot/start_airflow.sh"
sleep 5

# Iniciar Bot de Telegram
echo ""
echo "3. Iniciando Bot de Telegram..."
"$BASE_DIR/telegram_integration/start_bot.sh" &

echo ""
echo "=========================================="
echo "Sistema iniciado correctamente"
echo "=========================================="
echo ""
echo "Servicios disponibles:"
echo "  - Airflow UI: http://localhost:8080"
echo "  - Dask Dashboard: http://localhost:8787"
echo "  - Bot de Telegram: Activo"
echo ""
echo "Para detener el sistema: ./stop_bot_system.sh"
EOF

chmod +x "$PROJECT_ROOT/start_bot_system.sh"

# Crear script maestro de detención
cat > "$PROJECT_ROOT/stop_bot_system.sh" << 'EOF'
#!/bin/bash

echo "Deteniendo Sistema Bot Asistente CMMS..."

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$BASE_DIR/airflow_bot/stop_airflow.sh"
"$BASE_DIR/dask_cluster/stop_dask.sh"
pkill -f "telegram_integration/bot.py"

echo "Sistema detenido"
EOF

chmod +x "$PROJECT_ROOT/stop_bot_system.sh"

echo -e "${GREEN}✓ Scripts maestros creados${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}✓ Instalación completada${NC}"
echo "=========================================="
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Edita el archivo de configuración:"
echo "   $BASE_DIR/.env"
echo ""
echo "2. Configura los tokens de Telegram y GitHub"
echo ""
echo "3. Inicia el sistema completo:"
echo "   $PROJECT_ROOT/start_bot_system.sh"
echo ""
echo "4. Accede a Airflow UI:"
echo "   http://localhost:8080"
echo "   Usuario: admin"
echo "   Password: admin123"
echo ""
echo "5. Accede a Dask Dashboard:"
echo "   http://localhost:8787"
echo ""
echo "Para más información, consulta la documentación en:"
echo "   $PROJECT_ROOT/docs/bot_asistente/"
echo ""

