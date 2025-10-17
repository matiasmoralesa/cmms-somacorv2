#!/bin/bash
# Script para detener Apache Airflow

echo "=========================================="
echo "Deteniendo Apache Airflow"
echo "=========================================="
echo ""

# Detener webserver
echo "Deteniendo Airflow Webserver..."
pkill -f "airflow webserver"

# Detener scheduler
echo "Deteniendo Airflow Scheduler..."
pkill -f "airflow scheduler"

# Detener workers si existen
echo "Deteniendo Airflow Workers..."
pkill -f "airflow worker"

# Esperar un poco
sleep 2

# Verificar que se detuvieron
if pgrep -f "airflow" > /dev/null; then
    echo ""
    echo "⚠️  Algunos procesos de Airflow aún están corriendo:"
    ps aux | grep airflow | grep -v grep
    echo ""
    echo "Para forzar la detención:"
    echo "  pkill -9 -f airflow"
else
    echo ""
    echo "✅ Airflow detenido correctamente"
fi

echo ""

