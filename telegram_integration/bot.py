"""
Bot de Telegram para el Sistema CMMS Somacor v2
Proporciona notificaciones y comandos interactivos
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from loguru import logger

# Agregar directorios al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'airflow_bot'))
from config.airflow_config import TelegramConfig, LoggingConfig, CMSSConfig
from scripts.cmms_api_client import CMSSAPIClient

# Configurar logging
logger.add(
    LoggingConfig.LOG_FILE,
    format=LoggingConfig.FORMAT,
    level=LoggingConfig.LEVEL,
    rotation=LoggingConfig.ROTATION,
    retention=LoggingConfig.RETENTION
)


class TelegramBot:
    """Bot de Telegram para CMMS Somacor"""
    
    def __init__(self, token: str = None):
        """
        Inicializar bot de Telegram
        
        Args:
            token: Token del bot de Telegram
        """
        self.token = token or TelegramConfig.BOT_TOKEN
        self.cmms_client = CMSSAPIClient()
        self.application = None
        
        logger.info("Bot de Telegram inicializado")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Mensaje de bienvenida"""
        user = update.effective_user
        logger.info(f"Usuario {user.id} ({user.username}) ejecutó /start")
        
        welcome_message = f"""
🤖 **Bienvenido al Bot Asistente CMMS Somacor v2**

Hola {user.first_name}! 👋

Soy tu asistente inteligente para la gestión de mantenimiento. Puedo ayudarte con:

📊 **Monitoreo de Equipos**
- Ver estado de equipos
- Recibir alertas de fallas
- Análisis predictivo

🔧 **Órdenes de Trabajo**
- Consultar órdenes pendientes
- Crear nuevas órdenes
- Actualizar estados

📋 **Checklists**
- Revisar checklists completados
- Ver items críticos

📈 **Reportes**
- Generar reportes de KPIs
- Estadísticas por faena
- Métricas de desempeño

Usa /help para ver todos los comandos disponibles.
"""
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Mostrar ayuda"""
        logger.info(f"Usuario {update.effective_user.id} ejecutó /help")
        
        help_message = """
📚 **Comandos Disponibles**

**Información General:**
/start - Iniciar el bot
/help - Mostrar esta ayuda
/status - Ver estado del sistema

**Equipos:**
/equipos - Listar todos los equipos
/equipo <id> - Ver detalles de un equipo
/alertas - Ver alertas de equipos en riesgo

**Órdenes de Trabajo:**
/ordenes - Listar órdenes de trabajo
/orden <id> - Ver detalles de una orden
/pendientes - Ver órdenes pendientes
/crear_orden - Crear nueva orden de trabajo

**Checklists:**
/checklists - Ver checklists recientes
/checklist <id> - Ver detalles de un checklist

**Reportes:**
/reporte_diario - Generar reporte diario
/reporte_semanal - Generar reporte semanal
/kpis - Ver KPIs principales

**Configuración:**
/notificaciones - Configurar notificaciones
/preferencias - Configurar preferencias

Para más información sobre un comando específico, usa:
/help <comando>
"""
        
        await update.message.reply_text(
            help_message,
            parse_mode='Markdown'
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status - Ver estado del sistema"""
        logger.info(f"Usuario {update.effective_user.id} ejecutó /status")
        
        try:
            # Obtener estadísticas del dashboard
            stats = self.cmms_client.get_dashboard_stats()
            
            status_message = f"""
📊 **Estado del Sistema CMMS Somacor**

🔧 **Órdenes de Trabajo:**
- Pendientes: {stats.get('ordenes_pendientes', 0)}
- En Progreso: {stats.get('ordenes_en_progreso', 0)}
- Completadas (hoy): {stats.get('ordenes_completadas_hoy', 0)}

⚙️ **Equipos:**
- Total: {stats.get('total_equipos', 0)}
- Activos: {stats.get('equipos_activos', 0)}
- En Mantenimiento: {stats.get('equipos_en_mantenimiento', 0)}

⚠️ **Alertas:**
- Críticas: {stats.get('alertas_criticas', 0)}
- Advertencias: {stats.get('alertas_advertencia', 0)}

📅 **Última actualización:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
            
            await update.message.reply_text(
                status_message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error al obtener estado del sistema: {str(e)}")
            await update.message.reply_text(
                "❌ Error al obtener el estado del sistema. Por favor, intenta más tarde."
            )
    
    async def equipos_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /equipos - Listar equipos"""
        logger.info(f"Usuario {update.effective_user.id} ejecutó /equipos")
        
        try:
            # Obtener lista de equipos
            equipos = self.cmms_client.get_equipos()
            
            if not equipos:
                await update.message.reply_text("No se encontraron equipos.")
                return
            
            # Limitar a los primeros 10 equipos
            equipos_list = equipos[:10]
            
            message = "⚙️ **Lista de Equipos** (mostrando primeros 10)\n\n"
            
            for equipo in equipos_list:
                message += f"🔹 **{equipo.get('nombreequipo', 'N/A')}**\n"
                message += f"   ID: {equipo.get('idequipo')}\n"
                message += f"   Código: {equipo.get('codigointerno', 'N/A')}\n"
                message += f"   Tipo: {equipo.get('tipo_equipo_nombre', 'N/A')}\n"
                message += f"   Estado: {equipo.get('estado_actual_nombre', 'N/A')}\n\n"
            
            message += f"\nTotal de equipos: {len(equipos)}"
            message += "\n\nUsa /equipo <id> para ver detalles de un equipo específico."
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error al obtener equipos: {str(e)}")
            await update.message.reply_text(
                "❌ Error al obtener la lista de equipos. Por favor, intenta más tarde."
            )
    
    async def ordenes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ordenes - Listar órdenes de trabajo"""
        logger.info(f"Usuario {update.effective_user.id} ejecutó /ordenes")
        
        try:
            # Obtener lista de órdenes de trabajo
            ordenes = self.cmms_client.get_ordenes_trabajo()
            
            if not ordenes:
                await update.message.reply_text("No se encontraron órdenes de trabajo.")
                return
            
            # Limitar a las primeras 10 órdenes
            ordenes_list = ordenes[:10]
            
            message = "📋 **Órdenes de Trabajo** (mostrando primeras 10)\n\n"
            
            for orden in ordenes_list:
                estado_emoji = self._get_estado_emoji(orden.get('estado_ot_nombre', ''))
                prioridad_emoji = self._get_prioridad_emoji(orden.get('prioridad', ''))
                
                message += f"{estado_emoji} **{orden.get('codigoot', 'N/A')}** {prioridad_emoji}\n"
                message += f"   Equipo: {orden.get('equipo_nombre', 'N/A')}\n"
                message += f"   Tipo: {orden.get('tipo_mantenimiento_nombre', 'N/A')}\n"
                message += f"   Estado: {orden.get('estado_ot_nombre', 'N/A')}\n"
                message += f"   Técnico: {orden.get('usuario_asignado_nombre', 'No asignado')}\n\n"
            
            message += f"\nTotal de órdenes: {len(ordenes)}"
            message += "\n\nUsa /orden <id> para ver detalles de una orden específica."
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error al obtener órdenes de trabajo: {str(e)}")
            await update.message.reply_text(
                "❌ Error al obtener las órdenes de trabajo. Por favor, intenta más tarde."
            )
    
    async def pendientes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /pendientes - Ver órdenes pendientes"""
        logger.info(f"Usuario {update.effective_user.id} ejecutó /pendientes")
        
        try:
            # Obtener órdenes pendientes
            ordenes = self.cmms_client.get_ordenes_trabajo(params={'idestadoot': 1})
            
            if not ordenes:
                await update.message.reply_text("✅ No hay órdenes pendientes.")
                return
            
            message = f"⏳ **Órdenes Pendientes** ({len(ordenes)})\n\n"
            
            for orden in ordenes[:15]:  # Limitar a 15
                prioridad_emoji = self._get_prioridad_emoji(orden.get('prioridad', ''))
                
                message += f"{prioridad_emoji} **{orden.get('codigoot', 'N/A')}**\n"
                message += f"   Equipo: {orden.get('equipo_nombre', 'N/A')}\n"
                message += f"   Tipo: {orden.get('tipo_mantenimiento_nombre', 'N/A')}\n"
                message += f"   Prioridad: {orden.get('prioridad', 'N/A')}\n\n"
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error al obtener órdenes pendientes: {str(e)}")
            await update.message.reply_text(
                "❌ Error al obtener las órdenes pendientes. Por favor, intenta más tarde."
            )
    
    async def alertas_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /alertas - Ver alertas activas"""
        logger.info(f"Usuario {update.effective_user.id} ejecutó /alertas")
        
        # TODO: Implementar sistema de alertas basado en predicciones
        message = """
⚠️ **Alertas Activas**

🔴 **Críticas:**
- Equipo CAM-001: Alta probabilidad de falla (85%)
- Equipo RET-005: MTBF por debajo del umbral

🟡 **Advertencias:**
- Equipo CAR-003: Mantenimiento preventivo próximo
- Equipo SUP-002: Checklist con items fallidos

📊 Esta funcionalidad se completará con el sistema de análisis predictivo.
"""
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown'
        )
    
    async def kpis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /kpis - Ver KPIs principales"""
        logger.info(f"Usuario {update.effective_user.id} ejecutó /kpis")
        
        try:
            stats = self.cmms_client.get_dashboard_stats()
            
            message = f"""
📈 **KPIs Principales**

**Disponibilidad:**
- Equipos disponibles: {stats.get('disponibilidad_porcentaje', 0)}%
- Tiempo promedio de reparación: {stats.get('mttr_promedio', 0)} hrs

**Confiabilidad:**
- MTBF promedio: {stats.get('mtbf_promedio', 0)} días
- Tasa de fallas: {stats.get('tasa_fallas', 0)}%

**Eficiencia:**
- Órdenes completadas a tiempo: {stats.get('ordenes_a_tiempo_porcentaje', 0)}%
- Tiempo promedio de respuesta: {stats.get('tiempo_respuesta_promedio', 0)} hrs

**Productividad:**
- Órdenes completadas (mes): {stats.get('ordenes_completadas_mes', 0)}
- Promedio por técnico: {stats.get('promedio_ordenes_tecnico', 0)}

📅 Período: {datetime.now().strftime('%B %Y')}
"""
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error al obtener KPIs: {str(e)}")
            await update.message.reply_text(
                "❌ Error al obtener los KPIs. Por favor, intenta más tarde."
            )
    
    def _get_estado_emoji(self, estado: str) -> str:
        """Obtener emoji según el estado"""
        emojis = {
            'Pendiente': '⏳',
            'En Progreso': '🔧',
            'Completada': '✅',
            'Cancelada': '❌',
            'En Espera de Repuestos': '📦'
        }
        return emojis.get(estado, '📋')
    
    def _get_prioridad_emoji(self, prioridad: str) -> str:
        """Obtener emoji según la prioridad"""
        emojis = {
            'Urgente': '🔴',
            'Alta': '🟠',
            'Media': '🟡',
            'Baja': '🟢'
        }
        return emojis.get(prioridad, '⚪')
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejador de errores global"""
        logger.error(f"Error en el bot: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Ocurrió un error al procesar tu solicitud. Por favor, intenta más tarde."
            )
    
    def setup_handlers(self):
        """Configurar manejadores de comandos"""
        # Comandos básicos
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Comandos de equipos
        self.application.add_handler(CommandHandler("equipos", self.equipos_command))
        self.application.add_handler(CommandHandler("alertas", self.alertas_command))
        
        # Comandos de órdenes de trabajo
        self.application.add_handler(CommandHandler("ordenes", self.ordenes_command))
        self.application.add_handler(CommandHandler("pendientes", self.pendientes_command))
        
        # Comandos de reportes
        self.application.add_handler(CommandHandler("kpis", self.kpis_command))
        
        # Manejador de errores
        self.application.add_error_handler(self.error_handler)
        
        logger.info("Manejadores de comandos configurados")
    
    async def send_notification(
        self,
        chat_id: int,
        message: str,
        parse_mode: str = 'Markdown'
    ):
        """
        Enviar notificación a un usuario
        
        Args:
            chat_id: ID del chat de Telegram
            message: Mensaje a enviar
            parse_mode: Modo de parseo (Markdown o HTML)
        """
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info(f"Notificación enviada a chat_id: {chat_id}")
        except Exception as e:
            logger.error(f"Error al enviar notificación: {str(e)}")
    
    def run(self):
        """Iniciar el bot"""
        logger.info("Iniciando bot de Telegram...")
        
        # Crear aplicación
        self.application = Application.builder().token(self.token).build()
        
        # Configurar manejadores
        self.setup_handlers()
        
        # Iniciar bot
        logger.info("Bot de Telegram en ejecución")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Función principal"""
    bot = TelegramBot()
    bot.run()


if __name__ == '__main__':
    main()

