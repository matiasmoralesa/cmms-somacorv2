# Dockerfile para el backend de Django (somacor_cmms/backend)

# Usar una imagen base de Python
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=somacor_cmms.settings

# Establecer el directorio de trabajo
WORKDIR /app/somacor_cmms/backend

# Copiar el archivo de requisitos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer el puerto de Django
EXPOSE 8000

# Comando para ejecutar el servidor Gunicorn
# Se asume que Gunicorn está en requirements.txt
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "somacor_cmms.wsgi"]

