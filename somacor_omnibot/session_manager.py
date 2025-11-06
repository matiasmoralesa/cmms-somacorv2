# -*- coding: utf-8 -*-
"""
Módulo para gestionar sesiones de conversación utilizando Redis.
"""

import redis
import json
from datetime import timedelta

class RedisSessionManager:
    """Gestiona las sesiones de usuario en Redis."""

    def __init__(self, host='localhost', port=6379, db=0, session_ttl=3600):
        """
        Inicializa el gestor de sesiones de Redis.

        Args:
            host (str): Host de Redis.
            port (int): Puerto de Redis.
            db (int): Base de datos de Redis.
            session_ttl (int): Tiempo de vida de la sesión en segundos.
        """
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.session_ttl = timedelta(seconds=session_ttl)

    def get_session(self, user_id):
        """
        Obtiene la sesión de un usuario.

        Args:
            user_id (str): El ID del usuario.

        Returns:
            dict: Los datos de la sesión o None si no existe.
        """
        session_data = self.redis_client.get(f"session:{user_id}")
        if session_data:
            return json.loads(session_data)
        return None

    def save_session(self, user_id, session_data):
        """
        Guarda la sesión de un usuario.

        Args:
            user_id (str): El ID del usuario.
            session_data (dict): Los datos de la sesión a guardar.
        """
        self.redis_client.setex(
            f"session:{user_id}",
            self.session_ttl,
            json.dumps(session_data)
        )

    def delete_session(self, user_id):
        """
        Elimina la sesión de un usuario.

        Args:
            user_id (str): El ID del usuario.
        """
        self.redis_client.delete(f"session:{user_id}")

