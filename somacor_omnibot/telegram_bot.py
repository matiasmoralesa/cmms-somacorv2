#!/usr/bin/env python3
"""
Bot de Telegram para Somacor-CMMS

Este script conecta el bot de Telegram con el API Gateway usando polling.
Para desarrollo local y pruebas.
"""

import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_GATEWAY_URL = os.getenv('API_GATEWAY_URL', 'http://localhost:5001')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en las variables de entorno")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user_id = str(update.effective_chat.id)
    welcome_message = (
        "¡Hola! 👋 Soy el asistente virtual de Somacor-CMMS.\n\n"
        "Puedo ayudarte con:\n"
        "• Reportar fallas en equipos\n"
        "• Consultar estado de órdenes de trabajo\n"
        "• Listar equipos disponibles\n\n"
        "Escribe 'ayuda' para ver más opciones."
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    help_message = (
        "🤖 *Comandos disponibles:*\n\n"
        "/start - Iniciar conversación\n"
        "/help - Mostrar esta ayuda\n"
        "/status - Estado del sistema\n\n"
        "*Ejemplos de uso:*\n"
        "• 'reportar falla'\n"
        "• 'consultar estado OT-CORR-123'\n"
        "• 'listar equipos'\n"
        "• 'estado de la excavadora 01'\n"
    )
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status - Verificar estado del sistema"""
    try:
        # Verificar conectividad con API Gateway
        response = requests.get(f'{API_GATEWAY_URL}/health', timeout=5)
        if response.status_code == 200:
            status_message = "✅ Sistema operativo\n🔗 Conexión con API Gateway: OK"
        else:
            status_message = "⚠️ Sistema con problemas\n❌ API Gateway no responde correctamente"
    except requests.exceptions.RequestException:
        status_message = "❌ Sistema no disponible\n🔗 No se puede conectar con API Gateway"
    
    await update.message.reply_text(status_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja todos los mensajes de texto"""
    user_id = str(update.effective_chat.id)
    message = update.message.text
    
    logger.info(f"Mensaje recibido de {user_id}: {message}")
    
    try:
        # Enviar mensaje al API Gateway
        response = requests.post(
            f'{API_GATEWAY_URL}/api/bot/message',
            json={
                'user_id': user_id,
                'message': message,
                'platform': 'telegram'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            bot_response = response.json().get('response', 'Error procesando mensaje')
            await update.message.reply_text(bot_response)
        else:
            error_message = "❌ Error procesando tu mensaje. Intenta nuevamente."
            await update.message.reply_text(error_message)
            logger.error(f"Error del API Gateway: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        timeout_message = "⏱️ El sistema está procesando tu solicitud. Te notificaré cuando esté listo."
        await update.message.reply_text(timeout_message)
        logger.warning(f"Timeout procesando mensaje de {user_id}")
        
    except requests.exceptions.RequestException as e:
        error_message = "❌ No puedo conectar con el sistema. Intenta más tarde."
        await update.message.reply_text(error_message)
        logger.error(f"Error de conexión: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Maneja errores del bot"""
    logger.error(f"Error en el bot: {context.error}")
    
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Ocurrió un error inesperado. Por favor, intenta nuevamente."
        )

def main():
    """Función principal del bot"""
    logger.info("Iniciando bot de Telegram para Somacor-CMMS...")
    
    # Crear aplicación
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Añadir manejadores de comandos
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Añadir manejador de mensajes de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Añadir manejador de errores
    application.add_error_handler(error_handler)
    
    # Iniciar el bot
    logger.info("Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
