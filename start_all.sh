#!/bin/bash

# Script maestro para iniciar Backend y Frontend de CMMS Somacor v2
# Este script inicia ambos servicios en terminales separadas

echo "=========================================="
echo "CMMS Somacor v2 - Inicio Completo"
echo "=========================================="
echo ""

# Directorio del proyecto
PROJECT_DIR="$(dirname "$0")"
cd "$PROJECT_DIR"

echo "Directorio del proyecto: $PROJECT_DIR"
echo ""

# Verificar que los scripts existen
if [ ! -f "somacor_cmms/backend/start_backend.sh" ]; then
    echo "✗ Script de backend no encontrado"
    exit 1
fi

if [ ! -f "somacor_cmms/frontend/start_frontend.sh" ]; then
    echo "✗ Script de frontend no encontrado"
    exit 1
fi

echo "✓ Scripts encontrados"
echo ""
echo "=========================================="
echo "Instrucciones de inicio:"
echo "=========================================="
echo ""
echo "Para iniciar el sistema completo, ejecuta en terminales separadas:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd $PROJECT_DIR/somacor_cmms/backend"
echo "  ./start_backend.sh"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd $PROJECT_DIR/somacor_cmms/frontend"
echo "  ./start_frontend.sh"
echo ""
echo "=========================================="
echo "URLs de acceso:"
echo "=========================================="
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000/api/"
echo "Admin Django: http://localhost:8000/admin"
echo ""
echo "Usuario admin: admin / admin123"
echo ""
echo "=========================================="
echo "Base de datos: SQLite"
echo "Ubicación: somacor_cmms/backend/db.sqlite3"
echo "=========================================="
echo ""
echo "Nota: Para integración futura con Apache Airflow,"
echo "configura las variables de entorno en backend/.env"
echo ""

