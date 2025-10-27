# Dockerfile para el bot de Telegram (telegram_integration)

# Usar una imagen base de Python ligera
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app/telegram_integration

# Copiar el archivo de requisitos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación del bot
COPY . .

# Comando para ejecutar el bot
CMD ["python", "bot_v2.py"]

