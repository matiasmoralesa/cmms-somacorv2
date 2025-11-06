#!/bin/bash

# Script para configurar y ejecutar Apache Airflow para el proyecto Somacor-CMMS

echo "🚀 Configurando Apache Airflow para Somacor-CMMS..."

# Configurar variables de entorno de Airflow
export AIRFLOW_HOME=$(pwd)/airflow_home
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True
export AIRFLOW__CORE__EXECUTOR=LocalExecutor

# Crear directorio de Airflow si no existe
mkdir -p $AIRFLOW_HOME

echo "📁 Directorio de Airflow: $AIRFLOW_HOME"
echo "📁 Directorio de DAGs: $AIRFLOW__CORE__DAGS_FOLDER"

# Inicializar la base de datos de Airflow
echo "🗄️ Inicializando base de datos de Airflow..."
airflow db init

# Crear usuario administrador
echo "👤 Creando usuario administrador..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@somacor.com \
    --password admin123

echo "✅ Configuración completada!"
echo ""
echo "Para ejecutar Airflow:"
echo "1. Iniciar el scheduler: airflow scheduler"
echo "2. Iniciar el webserver: airflow webserver --port 8080"
echo "3. Acceder a la UI: http://localhost:8080"
echo "   Usuario: admin"
echo "   Contraseña: admin123"
echo ""
echo "Para probar un DAG manualmente:"
echo "airflow dags test complete_query_ot_workflow 2025-10-07"
