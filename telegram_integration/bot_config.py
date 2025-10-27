# Configuración de la API del CMMS para el bot de Telegram
import os
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000/api/v1/')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN') # Token proporcionado por el usuario
API_TOKEN = os.environ.get('API_TOKEN', 'YOUR_API_TOKEN')
API_TIMEOUT = 10
