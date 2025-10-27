# Guía de Despliegue en Google Cloud Platform (GCP) con Docker Compose

Esta guía asume que tienes una cuenta de GCP activa, el SDK de Google Cloud (`gcloud CLI`) instalado y configurado, y Docker y Docker Compose instalados en tu entorno local.

## 1. Configuración de Variables de Entorno

Antes de desplegar, debes configurar las variables sensibles en el archivo `.env` que se encuentra en la raíz del proyecto.

```bash
# Archivo: .env

# Token del Bot de Telegram
# Reemplazar con el token real
TELEGRAM_BOT_TOKEN=8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38

# Token de Autenticación para la API del CMMS (Backend)
# Reemplazar con un token de API válido generado desde el panel de administración de Django
API_TOKEN=YOUR_API_TOKEN

# Clave Secreta de Django (para el servicio 'backend')
# Reemplazar con una clave secreta segura (ej. generada con Django's get_random_secret_key())
SECRET_KEY=a_secure_secret_key_for_django
```

## 2. Despliegue en Google Compute Engine (GCE)

El método más sencillo para usar Docker Compose en GCP es a través de una instancia de Compute Engine.

### 2.1. Crear una Instancia de GCE

Utiliza la consola de GCP o el CLI para crear una instancia. Se recomienda usar una imagen de SO que ya tenga Docker preinstalado (como **Container-Optimized OS** o una imagen de Ubuntu/Debian con Docker instalado manualmente).

**Recomendación:** Para un despliegue rápido, puedes usar una imagen de Ubuntu y luego instalar Docker y Docker Compose:

```bash
# Ejemplo de comandos para instalar Docker y Docker Compose en Ubuntu
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER
# Reinicia la sesión o usa 'newgrp docker'

# Instalar Docker Compose (v2)
sudo apt-get install docker-compose-plugin
```

### 2.2. Transferir el Código Fuente

Transfiere todo el directorio del proyecto (`cmms-somacorv2`) a tu instancia de GCE.

```bash
gcloud compute scp --recurse /ruta/a/cmms-somacorv2/ username@instance-name:~/
```

### 2.3. Ejecutar el Despliegue

Conéctate a tu instancia de GCE a través de SSH.

```bash
gcloud compute ssh username@instance-name
```

Una vez dentro, navega al directorio del proyecto y ejecuta Docker Compose:

1.  **Construir las imágenes y levantar los servicios:**
    ```bash
    cd cmms-somacorv2
    docker compose up -d --build
    ```

2.  **Verificar el estado de los servicios:**
    ```bash
    docker compose ps
    ```
    Asegúrate de que los servicios `db`, `backend` y `telegram_bot` estén en estado `running` y que el `backend` esté accesible en el puerto 8000.

## 3. Configuración de Red y Firewall

Para acceder al backend de Django (si es necesario para webhooks o administración), debes abrir el puerto 8000 en el firewall de GCP.

1.  **Crea una regla de firewall en GCP:**
    ```bash
    gcloud compute firewall-rules create allow-http-8000 \
        --allow tcp:8000 \
        --source-ranges 0.0.0.0/0 \
        --target-tags http-server-8000 \
        --description "Permitir tráfico en el puerto 8000 para el backend de Django"
    ```
2.  **Aplica la etiqueta de red** (`http-server-8000`) a tu instancia de GCE.

## 4. Consideraciones Adicionales

*   **Base de Datos:** El `docker-compose.yml` utiliza un volumen local (`postgres_data`) para la persistencia de la base de datos. Para un entorno de producción, considera migrar la base de datos a un servicio gestionado de GCP como **Cloud SQL for PostgreSQL** para mayor fiabilidad y escalabilidad.
*   **Webhooks de Telegram:** Si utilizas webhooks, asegúrate de que la dirección IP pública de tu instancia de GCE esté configurada como el `API_BASE_URL` en el bot, y de que el puerto 8000 esté abierto. Si utilizas el modo *polling* (como está configurado el bot actualmente), no es necesario.
*   **Almacenamiento de Medios:** Para archivos estáticos y de medios, se recomienda utilizar **Google Cloud Storage (GCS)** en lugar del almacenamiento local del contenedor. Deberás configurar Django para usar GCS.
*   **Escalabilidad:** Para escalar el backend de Django, considera desplegarlo en **Google Kubernetes Engine (GKE)** o **Cloud Run**, que son soluciones más adecuadas para contenedores en producción.

---
**Archivos de Configuración Creados:**

*   `telegram_integration/Dockerfile`
*   `somacor_cmms/backend/Dockerfile`
*   `docker-compose.yml`
*   `.env` (con placeholders)
*   `GCP_DEPLOYMENT.md` (este archivo)

