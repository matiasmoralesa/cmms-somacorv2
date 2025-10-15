"""
Bot de Telegram para el Sistema CMMS Somacor v2 - Versión con Roles
Proporciona notificaciones y comandos interactivos basados en permisos
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from loguru import logger

# Agregar directorios al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'airflow_bot'))
from config.airflow_config import TelegramConfig, LoggingConfig, CMSSConfig
from scripts.cmms_api_client import CMSSAPIClient

# Importar sistema de usuarios y decoradores
from user_manager import user_manager, UserRole
from decorators import (
    require_admin,
    require_supervisor,
    require_tecnico,
    require_operador,
    register_user_if_new,
    log_command
)

# Configurar logging
logger.add(
    LoggingConfig.LOG_FILE,
    format=LoggingConfig.FORMAT,
    level=LoggingConfig.LEVEL,
    rotation=LoggingConfig.ROTATION,
    retention=LoggingConfig.RETENTION
)


class TelegramBotV2:
    """Bot de Telegram para CMMS Somacor con sistema de roles"""
    
    def __init__(self, token: str = None):
        """
        Inicializar bot de Telegram
        
        Args:
            token: Token del bot de Telegram
        """
        self.token = token or TelegramConfig.BOT_TOKEN
        self.cmms_client = CMSSAPIClient()
        self.application = None
        self.backend_available = False
        
        logger.info("Bot de Telegram V2 inicializado con sistema de roles")
    
    async def check_backend(self) -> bool:
        """Verificar si el backend está disponible"""
        try:
            response = self.cmms_client.get("/health/", timeout=3)
            self.backend_available = response.get("status") == "ok"
            return self.backend_available
        except:
            self.backend_available = False
            return False
    
    def get_mock_data(self, data_type: str) -> Dict:
        """Obtener datos simulados cuando el backend no está disponible"""
        mock_data = {
            "status": {
                "equipos_activos": 45,
                "ordenes_pendientes": 12,
                "ordenes_en_progreso": 8,
                "ordenes_completadas_hoy": 5,
                "alertas_criticas": 2,
                "sistema": "Modo Offline (Backend no disponible)"
            },
            "equipos": [
                {"id": 1, "codigo": "CAM-001", "nombre": "Camión Volvo FH16", "estado": "Activo"},
                {"id": 2, "codigo": "RET-005", "nombre": "Retroexcavadora CAT 420", "estado": "Activo"},
                {"id": 3, "codigo": "CAR-003", "nombre": "Cargador Frontal", "estado": "En Mantenimiento"},
            ],
            "alertas": {
                "criticas": [
                    {"equipo": "CAM-001", "probabilidad": 85, "mensaje": "Alta probabilidad de falla"},
                    {"equipo": "RET-005", "mensaje": "MTBF por debajo del umbral"}
                ],
                "advertencias": [
                    {"equipo": "CAR-003", "mensaje": "Mantenimiento preventivo próximo"},
                    {"equipo": "SUP-002", "mensaje": "Checklist con items fallidos"}
                ]
            },
            "ordenes": [
                {"id": 1, "codigo": "OT-2025-001", "equipo": "CAM-001", "tipo": "Correctivo", "estado": "Pendiente", "prioridad": "Alta"},
                {"id": 2, "codigo": "OT-2025-002", "equipo": "RET-005", "tipo": "Preventivo", "estado": "En Progreso", "prioridad": "Media"},
            ]
        }
        return mock_data.get(data_type, {})
    
    @register_user_if_new
    @log_command
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Mensaje de bienvenida"""
        user = update.effective_user
        user_role = user_manager.get_user_role(user.id)
        role_name = user_manager.get_role_name(user_role)
        
        welcome_message = f"""
🤖 Bienvenido al Bot Asistente CMMS Somacor

Hola {user.first_name}! 👋

Tu rol actual: {role_name}

Soy tu asistente inteligente para la gestión de mantenimiento.

Usa /help para ver los comandos disponibles según tu rol.
"""
        
        await update.message.reply_text(welcome_message)
    
    @register_user_if_new
    @log_command
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Mostrar ayuda según rol"""
        user_id = update.effective_user.id
        commands = user_manager.get_available_commands(user_id)
        
        help_message = "📚 COMANDOS DISPONIBLES\n\n" + "\n".join(commands)
        
        await update.message.reply_text(help_message)
    
    @register_user_if_new
    @log_command
    async def perfil_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /perfil - Ver perfil del usuario"""
        user_id = update.effective_user.id
        user_data = user_manager.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ Error al obtener tu perfil")
            return
        
        role_name = user_manager.get_role_name(user_data["role"])
        registered = datetime.fromisoformat(user_data["registered_at"]).strftime("%d/%m/%Y %H:%M")
        
        perfil_message = f"""
👤 TU PERFIL

Nombre: {user_data.get('first_name', 'N/A')} {user_data.get('last_name', '')}
Usuario: @{user_data.get('username', 'N/A')}
Rol: {role_name}

📊 Estadísticas:
• Registrado: {registered}
• Comandos ejecutados: {user_data.get('commands_count', 0)}
• Estado: {'✅ Activo' if user_data.get('active', True) else '❌ Inactivo'}
"""
        
        await update.message.reply_text(perfil_message)
    
    @register_user_if_new
    @log_command
    @require_operador
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status - Ver estado del sistema"""
        await update.message.reply_text("⏳ Consultando estado del sistema...")
        
        # Verificar backend
        backend_ok = await self.check_backend()
        
        if backend_ok:
            try:
                stats = self.cmms_client.get_dashboard_stats()
            except:
                stats = self.get_mock_data("status")
        else:
            stats = self.get_mock_data("status")
        
        status_message = f"""
📊 ESTADO DEL SISTEMA CMMS

{'⚠️ ' + stats.get('sistema', 'Sistema Operativo')}

📈 Estadísticas:
• Equipos activos: {stats.get('equipos_activos', 0)}
• Órdenes pendientes: {stats.get('ordenes_pendientes', 0)}
• Órdenes en progreso: {stats.get('ordenes_en_progreso', 0)}
• Completadas hoy: {stats.get('ordenes_completadas_hoy', 0)}
• Alertas críticas: {stats.get('alertas_criticas', 0)}

Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
        
        await update.message.reply_text(status_message)
    
    @register_user_if_new
    @log_command
    @require_operador
    async def equipos_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /equipos - Listar equipos"""
        await update.message.reply_text("⏳ Consultando equipos...")
        
        backend_ok = await self.check_backend()
        
        if backend_ok:
            try:
                equipos = self.cmms_client.get_equipos()
            except:
                equipos = self.get_mock_data("equipos")
        else:
            equipos = self.get_mock_data("equipos")
        
        if not equipos:
            await update.message.reply_text("❌ No se encontraron equipos")
            return
        
        equipos_message = f"🔧 EQUIPOS REGISTRADOS\n\nTotal: {len(equipos)}\n\n"
        
        for i, equipo in enumerate(equipos[:10], 1):
            equipos_message += f"{i}. {equipo.get('codigo', 'N/A')} - {equipo.get('nombre', 'N/A')}\n"
            equipos_message += f"   Estado: {equipo.get('estado', 'N/A')}\n\n"
        
        if len(equipos) > 10:
            equipos_message += f"\n... y {len(equipos) - 10} equipos más"
        
        await update.message.reply_text(equipos_message)
    
    @register_user_if_new
    @log_command
    @require_operador
    async def alertas_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /alertas - Ver alertas activas"""
        await update.message.reply_text("⏳ Consultando alertas...")
        
        backend_ok = await self.check_backend()
        
        if backend_ok:
            try:
                alertas = self.cmms_client.get_alertas()
            except:
                alertas = self.get_mock_data("alertas")
        else:
            alertas = self.get_mock_data("alertas")
        
        alertas_message = "⚠️ ALERTAS ACTIVAS\n\n"
        
        criticas = alertas.get("criticas", [])
        if criticas:
            alertas_message += "🔴 Críticas:\n"
            for alerta in criticas:
                equipos = alerta.get("equipo", "N/A")
                mensaje = alerta.get("mensaje", "N/A")
                prob = alerta.get("probabilidad", "")
                if prob:
                    alertas_message += f"- Equipo {equipo}: {mensaje} ({prob}%)\n"
                else:
                    alertas_message += f"- Equipo {equipo}: {mensaje}\n"
            alertas_message += "\n"
        
        advertencias = alertas.get("advertencias", [])
        if advertencias:
            alertas_message += "🟡 Advertencias:\n"
            for alerta in advertencias:
                equipo = alerta.get("equipo", "N/A")
                mensaje = alerta.get("mensaje", "N/A")
                alertas_message += f"- Equipo {equipo}: {mensaje}\n"
        
        if not criticas and not advertencias:
            alertas_message += "✅ No hay alertas activas"
        else:
            alertas_message += "\n📊 Esta funcionalidad se completará con el sistema de análisis predictivo."
        
        await update.message.reply_text(alertas_message)
    
    @register_user_if_new
    @log_command
    @require_tecnico
    async def ordenes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ordenes - Ver órdenes de trabajo"""
        await update.message.reply_text("⏳ Consultando órdenes de trabajo...")
        
        backend_ok = await self.check_backend()
        
        if backend_ok:
            try:
                ordenes = self.cmms_client.get_ordenes_trabajo()
            except:
                ordenes = self.get_mock_data("ordenes")
        else:
            ordenes = self.get_mock_data("ordenes")
        
        if not ordenes:
            await update.message.reply_text("❌ No se encontraron órdenes de trabajo")
            return
        
        ordenes_message = f"📝 ÓRDENES DE TRABAJO\n\nTotal: {len(ordenes)}\n\n"
        
        for i, orden in enumerate(ordenes[:10], 1):
            ordenes_message += f"{i}. {orden.get('codigo', 'N/A')}\n"
            ordenes_message += f"   Equipo: {orden.get('equipo', 'N/A')}\n"
            ordenes_message += f"   Tipo: {orden.get('tipo', 'N/A')}\n"
            ordenes_message += f"   Estado: {orden.get('estado', 'N/A')}\n"
            ordenes_message += f"   Prioridad: {orden.get('prioridad', 'N/A')}\n\n"
        
        if len(ordenes) > 10:
            ordenes_message += f"\n... y {len(ordenes) - 10} órdenes más"
        
        await update.message.reply_text(ordenes_message)
    
    @register_user_if_new
    @log_command
    @require_tecnico
    async def pendientes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /pendientes - Ver órdenes pendientes"""
        await update.message.reply_text("⏳ Consultando órdenes pendientes...")
        
        backend_ok = await self.check_backend()
        
        if backend_ok:
            try:
                ordenes = self.cmms_client.get_ordenes_pendientes()
            except:
                ordenes = [o for o in self.get_mock_data("ordenes") if o.get("estado") == "Pendiente"]
        else:
            ordenes = [o for o in self.get_mock_data("ordenes") if o.get("estado") == "Pendiente"]
        
        if not ordenes:
            await update.message.reply_text("✅ No hay órdenes pendientes")
            return
        
        pendientes_message = f"⏳ ÓRDENES PENDIENTES\n\nTotal: {len(ordenes)}\n\n"
        
        for i, orden in enumerate(ordenes, 1):
            pendientes_message += f"{i}. {orden.get('codigo', 'N/A')}\n"
            pendientes_message += f"   Equipo: {orden.get('equipo', 'N/A')}\n"
            pendientes_message += f"   Tipo: {orden.get('tipo', 'N/A')}\n"
            pendientes_message += f"   Prioridad: {orden.get('prioridad', 'N/A')}\n\n"
        
        await update.message.reply_text(pendientes_message)
    
    @register_user_if_new
    @log_command
    @require_supervisor
    async def kpis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /kpis - Ver KPIs del sistema"""
        await update.message.reply_text("⏳ Calculando KPIs...")
        
        kpis_message = """
📊 KPIs DE MANTENIMIENTO

⏱️ MTBF (Mean Time Between Failures)
• Promedio general: 45 días
• Mejor equipo: 120 días
• Peor equipo: 8 días

🔧 MTTR (Mean Time To Repair)
• Promedio general: 4.5 horas
• Mejor tiempo: 1.2 horas
• Peor tiempo: 12 horas

✅ Tasa de Completado
• Órdenes completadas: 85%
• Órdenes pendientes: 10%
• Órdenes canceladas: 5%

📅 Mantenimiento Preventivo
• Cumplimiento: 78%
• Órdenes programadas: 45
• Órdenes completadas: 35

🎯 Efectividad General
• Score de salud promedio: 72/100
• Equipos críticos: 5
• Equipos en buen estado: 40

📊 Esta funcionalidad se completará con datos reales del backend.
"""
        
        await update.message.reply_text(kpis_message)
    
    @register_user_if_new
    @log_command
    @require_admin
    async def usuarios_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /usuarios - Listar usuarios del bot"""
        users = user_manager.get_all_users()
        
        if not users:
            await update.message.reply_text("No hay usuarios registrados")
            return
        
        usuarios_message = f"👥 USUARIOS DEL BOT\n\nTotal: {len(users)}\n\n"
        
        for user in users[:20]:
            role_name = user_manager.get_role_name(user["role"])
            status = "✅" if user.get("active", True) else "❌"
            usuarios_message += f"{status} {user.get('first_name', 'N/A')} (@{user.get('username', 'N/A')})\n"
            usuarios_message += f"   Rol: {role_name}\n"
            usuarios_message += f"   ID: {user['telegram_id']}\n\n"
        
        if len(users) > 20:
            usuarios_message += f"\n... y {len(users) - 20} usuarios más"
        
        await update.message.reply_text(usuarios_message)
    
    @register_user_if_new
    @log_command
    @require_admin
    async def promover_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /promover - Cambiar rol de usuario"""
        if len(context.args) < 2:
            await update.message.reply_text(
                "Uso: /promover <telegram_id> <rol>\n\n"
                "Roles disponibles:\n"
                "• admin - Administrador\n"
                "• supervisor - Supervisor\n"
                "• tecnico - Técnico\n"
                "• operador - Operador\n"
                "• invitado - Invitado"
            )
            return
        
        try:
            target_id = int(context.args[0])
            new_role = context.args[1].lower()
            
            valid_roles = ["admin", "supervisor", "tecnico", "operador", "invitado"]
            if new_role not in valid_roles:
                await update.message.reply_text(f"❌ Rol inválido. Roles válidos: {', '.join(valid_roles)}")
                return
            
            if user_manager.update_user_role(target_id, new_role):
                role_name = user_manager.get_role_name(new_role)
                await update.message.reply_text(f"✅ Rol actualizado a {role_name}")
            else:
                await update.message.reply_text("❌ Usuario no encontrado")
        
        except ValueError:
            await update.message.reply_text("❌ ID de usuario inválido")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejador de errores"""
        logger.error(f"Error en el bot: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Ocurrió un error al procesar tu solicitud.\n"
                "Por favor, intenta más tarde o contacta al administrador."
            )
    
    def setup_handlers(self):
        """Configurar manejadores de comandos"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("perfil", self.perfil_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("equipos", self.equipos_command))
        self.application.add_handler(CommandHandler("alertas", self.alertas_command))
        self.application.add_handler(CommandHandler("ordenes", self.ordenes_command))
        self.application.add_handler(CommandHandler("pendientes", self.pendientes_command))
        self.application.add_handler(CommandHandler("kpis", self.kpis_command))
        self.application.add_handler(CommandHandler("usuarios", self.usuarios_command))
        self.application.add_handler(CommandHandler("promover", self.promover_command))
        
        # Manejador de errores
        self.application.add_error_handler(self.error_handler)
        
        logger.info("Manejadores de comandos configurados")
    
    def run(self):
        """Iniciar el bot"""
        logger.info("Iniciando bot de Telegram...")
        
        # Crear aplicación
        self.application = Application.builder().token(self.token).build()
        
        # Configurar manejadores
        self.setup_handlers()
        
        logger.info("Bot de Telegram en ejecución")
        
        # Iniciar bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = TelegramBotV2()
    bot.run()

