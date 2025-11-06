#!/bin/bash

# Script para detener todos los servicios del bot omnicanal

echo "🛑 Deteniendo Sistema Bot Omnicanal Somacor-CMMS"
echo "==============================================="

# Función para detener un servicio por PID
stop_service() {
    local service_name=$1
    local pid_file="${service_name,,}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat $pid_file)
        if kill -0 $pid 2>/dev/null; then
            echo "🛑 Deteniendo $service_name (PID: $pid)..."
            kill $pid
            sleep 2
            if kill -0 $pid 2>/dev/null; then
                echo "   Forzando detención..."
                kill -9 $pid
            fi
            rm $pid_file
            echo "✅ $service_name detenido"
        else
            echo "⚠️  $service_name ya no está ejecutándose"
            rm $pid_file
        fi
    else
        echo "❓ No se encontró archivo PID para $service_name"
    fi
}

# Detener servicios específicos
stop_service "API-Gateway"
stop_service "Airflow-Webserver"
stop_service "Airflow-Scheduler"

# Detener cualquier proceso restante de Airflow
echo ""
echo "🧹 Limpiando procesos restantes..."
pkill -f "airflow scheduler" 2>/dev/null && echo "   Scheduler de Airflow detenido"
pkill -f "airflow webserver" 2>/dev/null && echo "   Webserver de Airflow detenido"
pkill -f "api_gateway.py" 2>/dev/null && echo "   API Gateway detenido"
pkill -f "telegram_bot.py" 2>/dev/null && echo "   Bot de Telegram detenido"

echo ""
echo "✅ Todos los servicios han sido detenidos"
echo ""
echo "📝 Los logs se mantienen en el directorio 'logs/'"
echo "🚀 Para reiniciar el sistema: ./start_system.sh"
