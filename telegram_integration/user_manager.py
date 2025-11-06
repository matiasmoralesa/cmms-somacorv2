"""
Sistema de Gestión de Usuarios y Roles para el Bot de Telegram
Basado en los perfiles definidos en el documento de estado CMMS
"""

import json
from pathlib import Path
from typing import Optional, Dict, List
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
    
    def __init__(self, users_file: str = None):
        """
        Inicializar gestor de usuarios
        
        Args:
            users_file: Ruta al archivo JSON de usuarios
        """
        if users_file is None:
            users_file = Path(__file__).parent / "data" / "users.json"
        
        self.users_file = Path(users_file)
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.users = self._load_users()
        logger.info(f"UserManager inicializado con {len(self.users)} usuarios")
    
    def _load_users(self) -> Dict:
        """Cargar usuarios desde archivo JSON"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error al cargar usuarios: {e}")
                return {}
        return {}
    
    def _save_users(self):
        """Guardar usuarios en archivo JSON"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
            logger.info(f"Usuarios guardados: {len(self.users)}")
        except Exception as e:
            logger.error(f"Error al guardar usuarios: {e}")
    
    def register_user(
        self, 
        telegram_id: int, 
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        role: str = UserRole.INVITADO
    ) -> Dict:
        """
        Registrar un nuevo usuario
        
        Args:
            telegram_id: ID de Telegram del usuario
            username: Username de Telegram
            first_name: Nombre del usuario
            last_name: Apellido del usuario
            role: Rol del usuario
            
        Returns:
            Datos del usuario registrado
        """
        user_id = str(telegram_id)
        
        if user_id in self.users:
            logger.info(f"Usuario {telegram_id} ya existe")
            return self.users[user_id]
        
        user_data = {
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
            "registered_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "commands_count": 0,
            "active": True
        }
        
        self.users[user_id] = user_data
        self._save_users()
        
        logger.info(f"Usuario registrado: {telegram_id} ({username}) - Rol: {role}")
        return user_data
    
    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """
        Obtener datos de un usuario
        
        Args:
            telegram_id: ID de Telegram del usuario
            
        Returns:
            Datos del usuario o None si no existe
        """
        user_id = str(telegram_id)
        return self.users.get(user_id)
    
    def get_user_role(self, telegram_id: int) -> str:
        """
        Obtener el rol de un usuario
        
        Args:
            telegram_id: ID de Telegram del usuario
            
        Returns:
            Rol del usuario o INVITADO si no existe
        """
        user = self.get_user(telegram_id)
        if user:
            return user.get("role", UserRole.INVITADO)
        return UserRole.INVITADO
    
    def update_user_role(self, telegram_id: int, new_role: str) -> bool:
        """
        Actualizar el rol de un usuario
        
        Args:
            telegram_id: ID de Telegram del usuario
            new_role: Nuevo rol
            
        Returns:
            True si se actualizó correctamente
        """
        user_id = str(telegram_id)
        
        if user_id not in self.users:
            logger.warning(f"Usuario {telegram_id} no existe")
            return False
        
        old_role = self.users[user_id].get("role")
        self.users[user_id]["role"] = new_role
        self.users[user_id]["role_updated_at"] = datetime.now().isoformat()
        self._save_users()
        
        logger.info(f"Rol actualizado para {telegram_id}: {old_role} -> {new_role}")
        return True
    
    def update_last_seen(self, telegram_id: int):
        """Actualizar última vez visto"""
        user_id = str(telegram_id)
        
        if user_id in self.users:
            self.users[user_id]["last_seen"] = datetime.now().isoformat()
            self.users[user_id]["commands_count"] = self.users[user_id].get("commands_count", 0) + 1
            self._save_users()
    
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
        """Obtener todos los usuarios"""
        return list(self.users.values())
    
    def get_users_by_role(self, role: str) -> List[Dict]:
        """Obtener usuarios por rol"""
        return [user for user in self.users.values() if user.get("role") == role]
    
    def deactivate_user(self, telegram_id: int) -> bool:
        """Desactivar un usuario"""
        user_id = str(telegram_id)
        
        if user_id in self.users:
            self.users[user_id]["active"] = False
            self.users[user_id]["deactivated_at"] = datetime.now().isoformat()
            self._save_users()
            logger.info(f"Usuario desactivado: {telegram_id}")
            return True
        
        return False
    
    def activate_user(self, telegram_id: int) -> bool:
        """Activar un usuario"""
        user_id = str(telegram_id)
        
        if user_id in self.users:
            self.users[user_id]["active"] = True
            self.users[user_id]["activated_at"] = datetime.now().isoformat()
            self._save_users()
            logger.info(f"Usuario activado: {telegram_id}")
            return True
        
        return False
    
    def is_active(self, telegram_id: int) -> bool:
        """Verificar si el usuario está activo"""
        user = self.get_user(telegram_id)
        if user:
            return user.get("active", True)
        return False


# Instancia global del gestor de usuarios
user_manager = UserManager()

