# Visualización de Flujos en Apache Airflow

Este documento explica cómo visualizar y monitorear los flujos de trabajo (DAGs) del bot omnicanal en la interfaz de Apache Airflow.

## Configuración Inicial

### 1. Ejecutar el Script de Configuración

```bash
cd somacor_omnibot
./setup_airflow.sh
```

### 2. Iniciar Airflow

En terminales separadas, ejecutar:

```bash
# Terminal 1: Scheduler
airflow scheduler

# Terminal 2: Webserver
airflow webserver --port 8080
```

### 3. Acceder a la Interfaz Web

- **URL**: http://localhost:8080
- **Usuario**: admin
- **Contraseña**: admin123

## Flujos de Trabajo (DAGs) Implementados

### 1. `complete_query_ot_workflow` - Consulta de Órdenes de Trabajo

Este DAG demuestra el flujo completo de consulta de una OT:

```
start_workflow → extract_ot_number → validate_ot_number → query_cmms_api
                                                              ↓
end_workflow ← send_notification ← prepare_notification ← process_api_response
                                                              ↓
                                                        format_response
```

**Tareas del flujo:**

1. **start_workflow**: Inicio del proceso
2. **extract_ot_number**: Extrae el número de OT del mensaje usando regex
3. **validate_ot_number**: Valida que se encontró un número válido
4. **query_cmms_api**: Consulta la API del CMMS
5. **process_api_response**: Procesa la respuesta de la API
6. **format_response**: Formatea la información para el usuario
7. **prepare_notification**: Prepara los datos de notificación
8. **send_notification**: Envía la notificación al usuario
9. **end_workflow**: Fin del proceso

### 2. `process_user_message` - Enrutador Principal

DAG que analiza la intención del usuario y dispara el flujo apropiado.

### 3. `report_fault_workflow` - Reporte de Fallas

DAG para gestionar el proceso conversacional de reporte de fallas.

## Vistas Principales en Airflow UI

### 1. Vista de DAGs (Home)

- Lista todos los DAGs disponibles
- Muestra el estado de cada DAG (activo/pausado)
- Información de la última ejecución
- Botones para activar/pausar DAGs

### 2. Vista de Grafo (Graph View)

- Visualización gráfica del flujo de trabajo
- Muestra las dependencias entre tareas
- Colores indican el estado de cada tarea:
  - **Verde**: Éxito
  - **Rojo**: Fallo
  - **Amarillo**: En ejecución
  - **Gris**: No ejecutado

### 3. Vista de Gantt

- Línea de tiempo de ejecución de tareas
- Útil para identificar cuellos de botella
- Muestra duración de cada tarea

### 4. Vista de Logs

- Logs detallados de cada tarea
- Información de debugging
- Mensajes de error en caso de fallos

## Cómo Probar un Flujo

### Método 1: Desde la UI

1. Ir a la vista de DAGs
2. Hacer clic en el DAG deseado
3. Hacer clic en "Trigger DAG"
4. Configurar parámetros en el JSON:

```json
{
  "user_id": "test_user_123",
  "message": "consultar estado OT-CORR-001",
  "service_name": "telegram"
}
```

### Método 2: Desde la Línea de Comandos

```bash
# Probar un DAG específico
airflow dags test complete_query_ot_workflow 2025-10-07

# Probar una tarea específica
airflow tasks test complete_query_ot_workflow extract_ot_number 2025-10-07
```

## Monitoreo y Debugging

### Estados de las Tareas

- **success**: Tarea completada exitosamente
- **failed**: Tarea falló
- **retry**: Tarea en reintento
- **skipped**: Tarea omitida
- **up_for_retry**: Esperando reintento
- **running**: Tarea en ejecución

### Logs y Debugging

1. **Acceder a logs**: Hacer clic en una tarea → "Log"
2. **Ver detalles**: Información detallada de ejecución
3. **Reintentar tareas**: Botón "Retry" en tareas fallidas
4. **Limpiar estado**: "Clear" para resetear el estado de una tarea

## Configuración de Alertas

### Email en Fallos

Configurar en el DAG:

```python
default_args = {
    'email': ['admin@somacor.com'],
    'email_on_failure': True,
    'email_on_retry': False,
}
```

### Slack/Teams (Opcional)

Se pueden configurar webhooks para notificaciones en tiempo real.

## Métricas y Rendimiento

### Vista de Duración de Tareas

- Historial de duración de cada tarea
- Identificación de tendencias
- Detección de degradación de rendimiento

### Vista de Código

- Código fuente del DAG
- Documentación integrada
- Historial de cambios

## Mejores Prácticas para Visualización

1. **Usar nombres descriptivos** para tareas y DAGs
2. **Añadir documentación** con `doc_md`
3. **Agrupar tareas relacionadas** visualmente
4. **Usar DummyOperators** para puntos de control
5. **Configurar alertas** para fallos críticos

## Troubleshooting Común

### DAG no aparece en la UI

- Verificar sintaxis del archivo Python
- Revisar logs del scheduler
- Confirmar que el archivo está en el directorio de DAGs

### Tareas fallan constantemente

- Revisar logs detallados
- Verificar conectividad a APIs externas
- Validar configuración de variables de entorno

### Rendimiento lento

- Revisar configuración del executor
- Optimizar consultas a bases de datos
- Considerar paralelización de tareas
