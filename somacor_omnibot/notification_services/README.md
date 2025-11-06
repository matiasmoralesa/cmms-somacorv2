# Servicios de Notificación

Este módulo contiene los servicios para enviar notificaciones a través de diferentes plataformas de mensajería.

## Arquitectura

Se utiliza un patrón de Fábrica (`Factory`) para crear instancias de los servicios de notificación. Todos los servicios heredan de una clase base abstracta `BaseNotificationService` que define una interfaz común.

-   `base_service.py`: Define la clase `BaseNotificationService` con el método abstracto `send_message`.
-   `telegram_service.py`: Implementación del servicio de notificación para Telegram.
-   `factory.py`: Fábrica `get_notification_service` para obtener una instancia del servicio deseado.

## Cómo Añadir un Nuevo Servicio de Notificación

1.  **Crear un nuevo archivo de servicio**: Por ejemplo, `whatsapp_service.py`.
2.  **Implementar la clase del servicio**: La clase debe heredar de `BaseNotificationService` e implementar el método `send_message`.
3.  **Actualizar la fábrica**: Añadir la lógica para instanciar el nuevo servicio en `factory.py`.

## Endpoint de Notificaciones

El API Gateway expone un endpoint en `/api/notify` para enviar notificaciones. Este endpoint recibe un JSON con los siguientes parámetros:

-   `service_name`: El nombre del servicio (ej. "telegram").
-   `user_id`: El ID del usuario en la plataforma de mensajería.
-   `message`: El mensaje a enviar.

**Ejemplo de Petición:**

```bash
curl -X POST -H "Content-Type: application/json" \
-d 
{
    "service_name": "telegram",
    "user_id": "YOUR_TELEGRAM_CHAT_ID",
    "message": "Esta es una notificación de prueba."
}
 \
http://localhost:5001/api/notify
```

