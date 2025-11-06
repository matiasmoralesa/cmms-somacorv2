from .telegram_service import TelegramNotificationService

def get_notification_service(service_name: str):
    """
    Fábrica para obtener una instancia de un servicio de notificación.

    Args:
        service_name (str): El nombre del servicio de notificación (ej. 'telegram').

    Returns:
        BaseNotificationService: Una instancia del servicio de notificación.

    Raises:
        ValueError: Si el nombre del servicio no es válido.
    """
    if service_name == "telegram":
        return TelegramNotificationService()
    # Aquí se pueden añadir más servicios en el futuro, como 'whatsapp'
    # elif service_name == "whatsapp":
    #     return WhatsAppNotificationService()
    else:
        raise ValueError(f"Servicio de notificación no válido: {service_name}")

