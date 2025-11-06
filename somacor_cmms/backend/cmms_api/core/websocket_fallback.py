"""
Fallback para WebSockets cuando Redis no está disponible
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WebSocketFallback:
    """
    Fallback para cuando Redis no está disponible
    """
    
    @staticmethod
    def send_notification(group: str, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Fallback para enviar notificaciones cuando Redis no está disponible
        """
        logger.info(f"WebSocket Fallback - Group: {group}, Event: {event_type}, Data: {data}")
        return True
    
    @staticmethod
    def send_data_update(group: str, data_type: str, data: Dict[str, Any]) -> bool:
        """
        Fallback para enviar actualizaciones de datos cuando Redis no está disponible
        """
        logger.info(f"WebSocket Fallback - Group: {group}, DataType: {data_type}, Data: {data}")
        return True
