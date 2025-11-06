import os
import telegram
from .base_service import BaseNotificationService

class TelegramNotificationService(BaseNotificationService):
    """
    Servicio de notificación para enviar mensajes a través de Telegram.
    """

    def __init__(self):
        """
        Inicializa el servicio de notificaciones de Telegram.

        El token del bot de Telegram se obtiene de la variable de entorno TELEGRAM_BOT_TOKEN.
        """
        self.bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("La variable de entorno TELEGRAM_BOT_TOKEN no está configurada.")
        self.bot = telegram.Bot(token=self.bot_token)

    async def send_message(self, user_id: str, message: str):
        """
        Envía un mensaje a un usuario de Telegram.

        Args:
            user_id (str): El chat_id del usuario de Telegram.
            message (str): El mensaje a enviar.
        """
        try:
            await self.bot.send_message(chat_id=user_id, text=message)
            print(f"Mensaje enviado a {user_id} a través de Telegram.")
        except Exception as e:
            print(f"Error al enviar mensaje a {user_id} a través de Telegram: {e}")

