"""
Sistema de Gestión de Usuarios y Roles para el Bot de Telegram
Basado en los perfiles definidos en el documento de estado CMMS
"""

import json
from pathlib import Path
from typing import Optional, Dict, List
from cmms_api_client import CMSSAPIClient
CMMS_API_CLIENT = CMSSAPIClient()
from requests.exceptions import HTTPError
from datetime import datetime
from loguru import logger

class UserRole:
    """Roles de usuario basados en los perfiles del CMMS"""
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    TECNICO = "tecnico"
    OPERADOR = "operador"
    INVITADO = "invitado"

class UserManager:
    """Gestor de usuarios y permisos del bot"""
    
    def __init__(self):
        """
        Inicializar gestor de usuarios. La gestión de usuarios se realiza a través de la API de Django.
        """
        logger.info("UserManager inicializado para usar la API de Django")
    
    def _get_user_from_api(self, telegram_id: int) -> Optional[Dict]:
        """Obtiene el usuario del backend de Django por su ID de Telegram (campo 'telegram_id' en el modelo Usuario)"""
        try:
            # Asumiendo que el backend tiene un endpoint de búsqueda por telegram_id
            # Se usa get_usuarios con un filtro, asumiendo que el campo de filtro es 'telegram_id'
            users = CMMS_API_CLIENT.get_usuarios(params={'telegram_id': telegram_id})
            if users and isinstance(users, list):
                # El endpoint devuelve una lista, tomamos el primero
                return users[0]
            return None
        except HTTPError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Error HTTP al obtener usuario {telegram_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error al obtener usuario {telegram_id} de la API: {e}")
            return None

    
    def register_user(
        self, 
        telegram_id: int, 
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        role: str = UserRole.INVITADO
    ) -> Optional[Dict]:
        """
        Intenta obtener el usuario de la API. Si no existe, lo registra con el rol por defecto (INVITADO).
        
        Nota: El registro real de un usuario debe hacerse en la API de Django.
        Este método solo simula el registro inicial para obtener un rol.
        En un sistema real, se debería pedir al usuario que se vincule a su cuenta de CMMS.
        
        Args:
            telegram_id: ID de Telegram del usuario
            username: Username de Telegram
            first_name: Nombre del usuario
            last_name: Apellido del usuario
            role: Rol por defecto (INVITADO)
            
        Returns:
            Datos del usuario con su rol de la API o None si falla.
        """
        
        # 1. Intentar obtener el usuario de la API
        user_data = self._get_user_from_api(telegram_id)
        
        if user_data:
            logger.info(f"Usuario {telegram_id} encontrado en API. Rol: {user_data.get('rol_nombre', UserRole.INVITADO)}")
            return user_data

        # 2. Si no existe, se asume que es un nuevo usuario y se le asigna el rol de INVITADO
        # En un sistema real, se llamaría a un endpoint de registro/vinculación.
        # Aquí, simplemente se devuelve un objeto con el rol de INVITADO.
        # Se asume que el backend de Django tiene un campo 'telegram_id' para vincular.
        
        logger.warning(f"Usuario {telegram_id} no encontrado en API. Asignando rol de {UserRole.INVITADO}.")
        
        # Simulación de datos de usuario con rol INVITADO, ya que no se puede crear en la API sin más información
        # Se asume que el campo de rol en la API es 'rol_nombre' o similar.
        simulated_user_data = {
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "rol_nombre": UserRole.INVITADO, # Se usa 'rol_nombre' para mapear con la estructura de la API
            "idrol": 0, # Rol ID 0 para Invitado
            "last_seen": datetime.now().isoformat(),
        }
        
        return simulated_user_data
    
    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """
        Obtener datos de un usuario desde la API de Django.
        
        Args:
            telegram_id: ID de Telegram del usuario
            
        Returns:
            Datos del usuario de la API (incluyendo el rol) o None si no existe
        """
        # Se utiliza register_user, que intenta obtener el usuario y, si no lo encuentra,
        # devuelve un objeto simulado con el rol de INVITADO.
        return self.register_user(telegram_id)
    
    def get_user_role(self, telegram_id: int) -> str:
        """
        Obtener el rol de un usuario desde la API de Django.
        
        Args:
            telegram_id: ID de Telegram del usuario
            
        Returns:
            Rol del usuario (en minúsculas) o INVITADO si no existe
        """
        user = self.get_user(telegram_id)
        # Asumiendo que el campo de rol en la API es 'rol_nombre'
        if user:
            rol_api = user.get("rol_nombre", UserRole.INVITADO)
            return rol_api.lower()
        return UserRole.INVITADO
    
    def update_user_role(self, telegram_id: int, new_role: str) -> bool:
        """
        Actualizar el rol de un usuario en la API de Django.
        
        Nota: Este método es complejo porque requiere encontrar el ID interno del usuario en la API de Django
        y el ID del nuevo rol. Se simulará la lógica de actualización.
        
        Args:
            telegram_id: ID de Telegram del usuario
            new_role: Nuevo rol (string)
            
        Returns:
            True si se actualizó correctamente (simulado)
        """
        user = self._get_user_from_api(telegram_id)
        if not user:
            logger.warning(f"Usuario {telegram_id} no encontrado en API para actualizar rol.")
            return False
        
        # Lógica de mapeo de rol_nombre a idrol (Simulación)
        role_map = {
            UserRole.ADMIN: 4,
            UserRole.SUPERVISOR: 3,
            UserRole.TECNICO: 2,
            UserRole.OPERADOR: 1,
            UserRole.INVITADO: 0,
        }
        
        new_idrol = role_map.get(new_role.lower())
        
        if new_idrol is None:
            logger.error(f"Rol '{new_role}' no es un rol válido para la actualización.")
            return False
            
        try:
            # Asumiendo que el ID del usuario en la API es 'idusuario'
            user_api_id = user.get('idusuario')
            if not user_api_id:
                 logger.error(f"ID de usuario de la API no encontrado para {telegram_id}.")
                 return False
                 
            # Asumiendo que el endpoint de actualización es 'usuarios/{id}/' y se actualiza 'idrol'
            CMMS_API_CLIENT.update_usuario(user_api_id, {'idrol': new_idrol})
            
            logger.info(f"Rol actualizado en API para {telegram_id}: {user.get('rol_nombre')} -> {new_role}")
            return True
        except Exception as e:
            logger.error(f"Error al actualizar rol en la API para {telegram_id}: {e}")
            return False
    
    def update_last_seen(self, telegram_id: int):
        """
        Actualizar la última vez visto y el contador de comandos en la API de Django.
        
        Nota: Esta funcionalidad requiere un endpoint de la API para actualizar el perfil del usuario.
        Se simulará la llamada.
        """
        user = self._get_user_from_api(telegram_id)
        if not user:
            logger.warning(f"Usuario {telegram_id} no encontrado en API para actualizar last_seen.")
            return
            
        try:
            user_api_id = user.get('idusuario')
            if not user_api_id:
                 return
                 
            # Asumiendo que el campo para actualizar es 'last_seen' y 'commands_count'
            # Se asume que el backend maneja el incremento de commands_count
            CMMS_API_CLIENT.update_usuario(user_api_id, {'last_seen': datetime.now().isoformat()})
        except Exception as e:
            logger.error(f"Error al actualizar last_seen en la API para {telegram_id}: {e}")
    
    def is_admin(self, telegram_id: int) -> bool:
        """Verificar si el usuario es administrador"""
        return self.get_user_role(telegram_id) == UserRole.ADMIN
    
    def is_supervisor(self, telegram_id: int) -> bool:
        """Verificar si el usuario es supervisor o superior"""
        role = self.get_user_role(telegram_id)
        return role in [UserRole.ADMIN, UserRole.SUPERVISOR]
    
    def is_tecnico(self, telegram_id: int) -> bool:
        """Verificar si el usuario es técnico o superior"""
        role = self.get_user_role(telegram_id)
        return role in [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.TECNICO]
    
    def is_operador(self, telegram_id: int) -> bool:
        """Verificar si el usuario es operador o superior"""
        role = self.get_user_role(telegram_id)
        return role in [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.TECNICO, UserRole.OPERADOR]
    
    def has_permission(self, telegram_id: int, required_role: str) -> bool:
        """
        Verificar si el usuario tiene permisos
        
        Args:
            telegram_id: ID de Telegram del usuario
            required_role: Rol requerido
            
        Returns:
            True si tiene permisos
        """
        role_hierarchy = {
            UserRole.INVITADO: 0,
            UserRole.OPERADOR: 1,
            UserRole.TECNICO: 2,
            UserRole.SUPERVISOR: 3,
            UserRole.ADMIN: 4
        }
        
        user_role = self.get_user_role(telegram_id)
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def get_available_commands(self, telegram_id: int) -> List[str]:
        """
        Obtener comandos disponibles según el rol del usuario
        
        Args:
            telegram_id: ID de Telegram del usuario
            
        Returns:
            Lista de comandos disponibles
        """
        role = self.get_user_role(telegram_id)
        
        # Comandos básicos para todos
        commands = [
            "/start - Iniciar el bot",
            "/help - Mostrar ayuda",
            "/perfil - Ver tu perfil",
        ]
        
        # Comandos para operadores y superiores
        if self.is_operador(telegram_id):
            commands.extend([
                "",
                "📊 Monitoreo:",
                "/status - Estado del sistema",
                "/equipos - Lista de equipos",
                "/alertas - Alertas activas",
            ])
        
        # Comandos para técnicos y superiores
        if self.is_tecnico(telegram_id):
            commands.extend([
                "",
                "🔧 Órdenes de Trabajo:",
                "/ordenes - Mis órdenes de trabajo",
                "/pendientes - Órdenes pendientes",
                "/completar [id] - Completar orden",
            ])
        
        # Comandos para supervisores y superiores
        if self.is_supervisor(telegram_id):
            commands.extend([
                "",
                "📋 Gestión:",
                "/todas_ordenes - Todas las órdenes",
                "/asignar [id] [tecnico] - Asignar orden",
                "/kpis - KPIs del sistema",
                "/reportes - Generar reportes",
            ])
        
        # Comandos solo para administradores
        if self.is_admin(telegram_id):
            commands.extend([
                "",
                "⚙️ Administración:",
                "/usuarios - Lista de usuarios",
                "/promover [id] [rol] - Cambiar rol",
                "/config - Configuración del bot",
            ])
        
        return commands
    
    def get_role_name(self, role: str) -> str:
        """Obtener nombre legible del rol"""
        role_names = {
            UserRole.ADMIN: "👑 Administrador",
            UserRole.SUPERVISOR: "👔 Supervisor",
            UserRole.TECNICO: "🔧 Técnico",
            UserRole.OPERADOR: "👷 Operador",
            UserRole.INVITADO: "👤 Invitado"
        }
        return role_names.get(role, "👤 Desconocido")
    
    def get_all_users(self) -> List[Dict]:
        """Obtener todos los usuarios de la API"""
        try:
            return CMMS_API_CLIENT.get_usuarios()
        except Exception as e:
            logger.error(f"Error al obtener todos los usuarios de la API: {e}")
            return []
    
    def get_users_by_role(self, role: str) -> List[Dict]:
        """Obtener usuarios por rol de la API"""
        # Mapeo inverso de rol_nombre a idrol (Simulación)
        role_map = {
            UserRole.ADMIN: 4,
            UserRole.SUPERVISOR: 3,
            UserRole.TECNICO: 2,
            UserRole.OPERADOR: 1,
            UserRole.INVITADO: 0,
        }
        
        idrol = role_map.get(role.lower())
        if idrol is None:
            logger.warning(f"Rol '{role}' no es un rol válido para la búsqueda.")
            return []
            
        try:
            # Asumiendo que el endpoint de usuarios acepta el filtro 'idrol'
            return CMMS_API_CLIENT.get_usuarios(params={'idrol': idrol})
        except Exception as e:
            logger.error(f"Error al obtener usuarios por rol '{role}' de la API: {e}")
            return []
    
    def deactivate_user(self, telegram_id: int) -> bool:
        """Desactivar un usuario en la API (Simulación)"""
        logger.warning("Funcionalidad de desactivación de usuario no implementada en la API de forma directa. Se requiere un endpoint PATCH para el campo 'active'.")
        return False
    
    def activate_user(self, telegram_id: int) -> bool:
        """Activar un usuario en la API (Simulación)"""
        logger.warning("Funcionalidad de activación de usuario no implementada en la API de forma directa. Se requiere un endpoint PATCH para el campo 'active'.")
        return False
    
    def is_active(self, telegram_id: int) -> bool:
        """Verificar si el usuario está activo (asumiendo que los usuarios de la API están activos por defecto)"""
        user = self.get_user(telegram_id)
        # Asumimos que si el usuario existe en la API, está activo.
        return bool(user)


# Instancia global del gestor de usuarios
user_manager = UserManager()



# Instancia global para usar en el bot
user_manager = UserManager()

