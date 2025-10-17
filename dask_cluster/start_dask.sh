#!/bin/bash
# Script para iniciar Dask Cluster

echo "=========================================="
echo "Iniciando Dask Cluster"
echo "=========================================="
echo ""

# Directorio del proyecto
cd "$(dirname "$0")"

# Crear directorio de logs
mkdir -p logs

# Configuración
SCHEDULER_PORT=8786
DASHBOARD_PORT=8787
N_WORKERS=4

echo "Configuración:"
echo "  Scheduler port: $SCHEDULER_PORT"
echo "  Dashboard port: $DASHBOARD_PORT"
echo "  Workers: $N_WORKERS"
echo ""

# Iniciar Dask Scheduler
echo "Iniciando Dask Scheduler..."
nohup dask scheduler --port $SCHEDULER_PORT --dashboard-address :$DASHBOARD_PORT > logs/scheduler.log 2>&1 &
SCHEDULER_PID=$!
echo "  PID: $SCHEDULER_PID"
echo "  Dashboard: http://localhost:$DASHBOARD_PORT"

# Esperar a que el scheduler esté listo
sleep 3

# Iniciar Dask Workers
echo ""
echo "Iniciando $N_WORKERS Dask Workers..."
for i in $(seq 1 $N_WORKERS); do
    nohup dask worker tcp://localhost:$SCHEDULER_PORT --nthreads 2 --memory-limit 2GB > logs/worker_$i.log 2>&1 &
    WORKER_PID=$!
    echo "  Worker $i PID: $WORKER_PID"
done

echo ""
echo "=========================================="
echo "Dask Cluster iniciado correctamente"
echo "=========================================="
echo ""
echo "URLs:"
echo "  Dashboard: http://localhost:$DASHBOARD_PORT"
echo "  Scheduler: tcp://localhost:$SCHEDULER_PORT"
echo ""
echo "Procesos:"
echo "  Scheduler PID: $SCHEDULER_PID"
echo "  Workers: $N_WORKERS"
echo ""
echo "Logs:"
echo "  Scheduler: $(pwd)/logs/scheduler.log"
echo "  Workers: $(pwd)/logs/worker_*.log"
echo ""
echo "Para detener Dask:"
echo "  ./stop_dask.sh"
echo ""
echo "Para ver el dashboard:"
echo "  Abre http://localhost:$DASHBOARD_PORT en tu navegador"
echo ""

