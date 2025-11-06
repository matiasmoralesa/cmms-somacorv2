_service.py`
"""
Módulo que define la clase base para los servicios de notificación.
"""

from abc import ABC, abstractmethod

class BaseNotificationService(ABC):
    """
    Clase base abstracta para los servicios de notificación.

    Todos los servicios de notificación deben heredar de esta clase e implementar
    el método `send_message`.
    """

    @abstractmethod
    def send_message(self, user_id: str, message: str):
        """
        Envía un mensaje a un usuario.

        Args:
            user_id (str): El ID del usuario en la plataforma de mensajería.
            message (str): El mensaje a enviar.

        Raises:
            NotImplementedError: Si el método no se implementa en la subclase.
        """
        raise NotImplementedError("El método send_message debe ser implementado por la subclase.")

