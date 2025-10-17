#!/bin/bash
# Script para detener Dask Cluster

echo "=========================================="
echo "Deteniendo Dask Cluster"
echo "=========================================="
echo ""

# Detener workers
echo "Deteniendo Dask Workers..."
pkill -f "dask worker"

# Detener scheduler
echo "Deteniendo Dask Scheduler..."
pkill -f "dask scheduler"

# Esperar un poco
sleep 2

# Verificar que se detuvieron
if pgrep -f "dask" > /dev/null; then
    echo ""
    echo "⚠️  Algunos procesos de Dask aún están corriendo:"
    ps aux | grep dask | grep -v grep
    echo ""
    echo "Para forzar la detención:"
    echo "  pkill -9 -f dask"
else
    echo ""
    echo "✅ Dask Cluster detenido correctamente"
fi

echo ""

