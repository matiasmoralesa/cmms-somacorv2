#!/bin/bash

# Script de inicio para el backend de CMMS Somacor v2
# Este script configura y ejecuta el servidor de desarrollo de Django

echo "==================================="
echo "CMMS Somacor v2 - Backend Startup"
echo "==================================="
echo ""

# Directorio del proyecto
cd "$(dirname "$0")"

# Cargar variables de entorno
if [ -f .env ]; then
    echo "✓ Cargando variables de entorno desde .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠ Archivo .env no encontrado, usando valores por defecto"
fi

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "✗ Python3 no está instalado"
    exit 1
fi

echo "✓ Python3 encontrado: $(python3 --version)"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo ""
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "✓ Activando entorno virtual"
source venv/bin/activate

# Verificar que las dependencias están instaladas
echo ""
echo "Verificando dependencias..."
if ! python -c "import django" &> /dev/null; then
    echo "⚠ Django no está instalado. Instalando dependencias..."
    pip install -r requirements.txt
    pip install django-filter channels channels-redis
else
    echo "✓ Dependencias verificadas"
fi

# Crear directorio de logs si no existe
mkdir -p logs
mkdir -p media

# Aplicar migraciones
echo ""
echo "Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

# Crear superusuario si no existe (solo para desarrollo)
echo ""
echo "Verificando superusuario..."
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@somacor.cl', 'admin123')" 2>/dev/null || echo "✓ Superusuario ya existe"

# Recolectar archivos estáticos (opcional en desarrollo)
# python manage.py collectstatic --noinput

echo ""
echo "==================================="
echo "Iniciando servidor de desarrollo..."
echo "==================================="
echo "Base de datos: SQLite (db.sqlite3)"
echo "URL: http://localhost:8000"
echo "Admin: http://localhost:8000/admin"
echo "API: http://localhost:8000/api/"
echo "API V2: http://localhost:8000/api/v2/"
echo ""
echo "Usuario admin: admin / admin123"
echo ""
echo "Estadísticas de la BD:"
echo "- Equipos: $(sqlite3 db.sqlite3 'SELECT COUNT(*) FROM equipos')"
echo "- Faenas: $(sqlite3 db.sqlite3 'SELECT COUNT(*) FROM faenas')"
echo "- Usuarios: $(sqlite3 db.sqlite3 'SELECT COUNT(*) FROM auth_user')"
echo "==================================="
echo ""

# Iniciar servidor de desarrollo
python manage.py runserver 0.0.0.0:8000

