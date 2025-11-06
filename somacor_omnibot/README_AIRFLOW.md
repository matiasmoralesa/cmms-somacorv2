# Arquitectura del Bot Omnicanal con Apache Airflow

Esta documentación describe la nueva arquitectura del bot omnicanal de Somacor-CMMS, que utiliza Apache Airflow para orquestar flujos de trabajo complejos y un API Gateway en Flask para gestionar las interacciones en tiempo real.

## 1. Arquitectura General

La nueva arquitectura sigue un enfoque híbrido para combinar la robustez de Airflow con la baja latencia de Flask para interacciones conversacionales.

```
+----------------+      +---------------------+      +------------------+      +----------------+
|                |      |                     |      |                  |      |                |
| Frontend/User  |----->|   API Gateway       |----->|  Apache Airflow  |----->|    CMMS API    |
| (Chat, WhatsApp)|      |     (Flask)         |      |   (DAGs)         |      |    (Django)    |
|                |      |                     |      |                  |      |                |
+----------------+      +---------+-----------+      +--------+---------+      +----------------+
                        |           ^                        |
                        |           |                        |
                        |  Simple   |  Complex               |  Webhook
                        |  Request  |  Request               |  Response
                        |           |                        |
                        +-----------+------------------------+

```

**Componentes:**

-   **API Gateway (Flask)**: Punto de entrada para todos los mensajes. Gestiona las sesiones de usuario con Redis. Responde directamente a las solicitudes simples y dispara DAGs de Airflow para las complejas.
-   **Apache Airflow**: Orquesta los flujos de trabajo complejos (DAGs) como el reporte de fallas. Se comunica con la API del CMMS y envía la respuesta final a través de un webhook.
-   **Redis**: Almacena las sesiones de conversación para un acceso rápido y persistente.
-   **CMMS API (Django)**: La API de backend existente que gestiona la lógica de negocio.

## 2. Flujo de Datos

1.  El **Usuario** envía un mensaje.
2.  El **API Gateway** lo recibe y analiza la intención.
    -   **Si la intención es simple** (ej. un saludo), responde inmediatamente.
    -   **Si la intención es compleja** (ej. reportar una falla), dispara el DAG correspondiente en Airflow y notifica al usuario que la solicitud se está procesando.
3.  **Airflow** ejecuta el DAG de forma asíncrona, realizando los pasos necesarios (consultar la API del CMMS, etc.).
4.  Al finalizar, la última tarea del DAG envía la respuesta a un **endpoint de webhook** en el API Gateway.
5.  El API Gateway recibe la respuesta y la reenvía al usuario a través del canal original (e.g., WebSockets).

## 3. Cómo Ejecutar el Sistema

### Prerrequisitos

-   Docker y Docker Compose
-   Python 3.11+
-   Apache Airflow instalado y configurado
-   Redis

### Pasos

1.  **Iniciar los servicios de backend**:

    ```bash
    # Iniciar la base de datos y la API del CMMS (desde el directorio raíz del proyecto)
    docker-compose up -d db cmms_api
    ```

2.  **Iniciar Redis**:

    ```bash
    docker run -d -p 6379:6379 --name redis_somacor redis
    ```

3.  **Configurar y Ejecutar Airflow**:

    -   Asegúrese de que su `airflow.cfg` apunte al directorio `somacor_omnibot/dags`.
    -   Inicie el scheduler y el webserver de Airflow.

    ```bash
    airflow scheduler
    airflow webserver
    ```

4.  **Iniciar el API Gateway**:

    ```bash
    cd somacor_omnibot
    python api_gateway.py
    ```

5.  **Probar la Interacción**:

    Envíe una petición POST a `http://localhost:5001/api/bot/message` con un JSON como el siguiente:

    ```json
    {
        "user_id": "test_user_123",
        "message": "consultar estado de OT-CORR-1"
    }
    ```

    Recibirá una respuesta inmediata indicando que la solicitud se está procesando. La respuesta final del DAG se imprimirá en la consola del `api_gateway.py` al ser recibida por el webhook.

## 4. Ventajas de esta Arquitectura

-   **Baja Latencia**: Las interacciones simples son instantáneas.
-   **Robustez**: Los flujos complejos se benefician de la fiabilidad y los reintentos de Airflow.
-   **Escalabilidad**: Cada componente puede escalar de forma independiente.
-   **Monitoreo**: La UI de Airflow proporciona una visibilidad completa de la ejecución de los flujos de trabajo.

