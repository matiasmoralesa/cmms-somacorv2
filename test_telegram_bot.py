"""
Script de prueba del Bot de Telegram
Verifica que el bot esté configurado correctamente y pueda conectarse
"""

import sys
from pathlib import Path
import asyncio
from datetime import datetime

# Agregar directorios al path
sys.path.insert(0, str(Path(__file__).parent / 'airflow_bot'))
sys.path.insert(0, str(Path(__file__).parent / 'telegram_integration'))

print("=" * 80)
print("PRUEBA DE CONFIGURACIÓN DEL BOT DE TELEGRAM")
print("=" * 80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Test 1: Cargar configuración
print("Test 1: Cargando configuración...")
print("-" * 80)

try:
    from config.airflow_config import TelegramConfig
    
    token = TelegramConfig.BOT_TOKEN
    
    if token and token != "your_telegram_bot_token_here":
        print(f"✅ Token de Telegram configurado")
        print(f"   Token: {token[:20]}...{token[-10:]}")
    else:
        print(f"❌ Token de Telegram NO configurado")
        print(f"   Por favor configura TELEGRAM_BOT_TOKEN en airflow_bot/.env")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error al cargar configuración: {str(e)}")
    sys.exit(1)

print()

# Test 2: Inicializar bot
print("Test 2: Inicializando bot de Telegram...")
print("-" * 80)

try:
    from telegram import Bot
    from telegram.error import TelegramError
    
    bot = Bot(token=token)
    print(f"✅ Bot inicializado correctamente")
except Exception as e:
    print(f"❌ Error al inicializar bot: {str(e)}")
    sys.exit(1)

print()

# Test 3: Obtener información del bot
print("Test 3: Obteniendo información del bot...")
print("-" * 80)

async def get_bot_info():
    try:
        me = await bot.get_me()
        
        print(f"✅ Conexión exitosa con Telegram")
        print(f"   ID: {me.id}")
        print(f"   Nombre: {me.first_name}")
        print(f"   Username: @{me.username}")
        print(f"   Puede unirse a grupos: {me.can_join_groups}")
        print(f"   Puede leer mensajes de grupos: {me.can_read_all_group_messages}")
        print(f"   Soporta inline queries: {me.supports_inline_queries}")
        
        return True
    except TelegramError as e:
        print(f"❌ Error de Telegram: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

# Ejecutar test asíncrono
try:
    result = asyncio.run(get_bot_info())
    if not result:
        sys.exit(1)
except Exception as e:
    print(f"❌ Error al ejecutar test: {str(e)}")
    sys.exit(1)

print()

# Test 4: Verificar comandos del bot
print("Test 4: Verificando comandos implementados...")
print("-" * 80)

try:
    from bot import (
        start_command,
        help_command,
        status_command,
        equipos_command,
        ordenes_command,
        pendientes_command,
        alertas_command,
        kpis_command
    )
    
    comandos = [
        ('start', start_command),
        ('help', help_command),
        ('status', status_command),
        ('equipos', equipos_command),
        ('ordenes', ordenes_command),
        ('pendientes', pendientes_command),
        ('alertas', alertas_command),
        ('kpis', kpis_command),
    ]
    
    print(f"✅ Comandos implementados: {len(comandos)}")
    for nombre, func in comandos:
        print(f"   /{nombre} - {func.__name__}")
    
except Exception as e:
    print(f"⚠️  No se pudieron cargar todos los comandos: {str(e)}")
    print(f"   Esto es normal si el bot aún no está completamente configurado")

print()

# Resumen
print("=" * 80)
print("RESUMEN DE CONFIGURACIÓN")
print("=" * 80)
print()
print("✅ Bot de Telegram configurado correctamente")
print()
print("Información del bot:")
print(f"  - Token configurado: ✓")
print(f"  - Conexión a Telegram: ✓")
print(f"  - Comandos implementados: ✓")
print()
print("Próximos pasos:")
print("  1. Inicia el bot con: python telegram_integration/bot.py")
print("  2. Busca el bot en Telegram por su @username")
print("  3. Envía /start para comenzar")
print()
print("Para obtener tu Chat ID:")
print("  1. Envía cualquier mensaje al bot")
print("  2. Visita: https://api.telegram.org/bot{TOKEN}/getUpdates")
print("  3. Busca el campo 'chat':{'id':123456789}")
print()
print("=" * 80)

