"""
Decoradores para verificar permisos y roles en comandos del bot
"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from user_manager import user_manager, UserRole


def require_role(required_role: str):
    """
    Decorador para requerir un rol específico
    
    Args:
        required_role: Rol mínimo requerido
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            username = update.effective_user.username or update.effective_user.first_name
            
            # Verificar si el usuario tiene permisos
            if not user_manager.has_permission(user_id, required_role):
                user_role = user_manager.get_user_role(user_id)
                role_name = user_manager.get_role_name(user_role)
                required_name = user_manager.get_role_name(required_role)
                
                logger.warning(
                    f"Usuario {user_id} ({username}) intentó ejecutar {func.__name__} "
                    f"sin permisos (tiene {role_name}, requiere {required_name})"
                )
                
                await update.message.reply_text(
                    f"❌ Acceso denegado\n\n"
                    f"Tu rol actual: {role_name}\n"
                    f"Rol requerido: {required_name}\n\n"
                    f"Contacta a un administrador para solicitar permisos."
                )
                return
            
            # Ejecutar el comando
            return await func(self, update, context)
        
        return wrapper
    return decorator


def require_admin(func):
    """Decorador para requerir rol de administrador"""
    return require_role(UserRole.ADMIN)(func)


def require_supervisor(func):
    """Decorador para requerir rol de supervisor o superior"""
    return require_role(UserRole.SUPERVISOR)(func)


def require_tecnico(func):
    """Decorador para requerir rol de técnico o superior"""
    return require_role(UserRole.TECNICO)(func)


def require_operador(func):
    """Decorador para requerir rol de operador o superior"""
    return require_role(UserRole.OPERADOR)(func)


def register_user_if_new(func):
    """
    Decorador para registrar automáticamente usuarios nuevos
    """
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        # Verificar si el usuario existe
        existing_user = user_manager.get_user(user.id)
        
        if not existing_user:
            # Registrar nuevo usuario como invitado
            user_manager.register_user(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                role=UserRole.INVITADO
            )
            
            logger.info(f"Nuevo usuario registrado: {user.id} ({user.username})")
            
            # Notificar al usuario
            await update.message.reply_text(
                f"👋 ¡Bienvenido {user.first_name}!\n\n"
                f"Has sido registrado como usuario invitado.\n"
                f"Contacta a un administrador para obtener más permisos.\n\n"
                f"Usa /help para ver los comandos disponibles."
            )
        else:
            # Actualizar última vez visto
            user_manager.update_last_seen(user.id)
        
        # Verificar si el usuario está activo
        if not user_manager.is_active(user.id):
            await update.message.reply_text(
                "❌ Tu cuenta ha sido desactivada.\n\n"
                "Contacta a un administrador para más información."
            )
            return
        
        # Ejecutar el comando
        return await func(self, update, context)
    
    return wrapper


def log_command(func):
    """Decorador para registrar ejecución de comandos"""
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        command = update.message.text
        
        logger.info(
            f"Comando ejecutado: {command} | "
            f"Usuario: {user.id} ({user.username}) | "
            f"Rol: {user_manager.get_role_name(user_manager.get_user_role(user.id))}"
        )
        
        return await func(self, update, context)
    
    return wrapper

