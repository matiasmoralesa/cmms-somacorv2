# Sistema CMMS Somacor

Este repositorio contiene el código fuente del Sistema de Gestión de Mantenimiento Computarizado (CMMS) desarrollado para Somacor. El sistema está diseñado para optimizar la gestión de equipos, órdenes de trabajo, planes de mantenimiento y checklists, mejorando la eficiencia operativa y la trazabilidad de las actividades de mantenimiento con un bot ia asistente.

## 🚀 Características Principales

- **Gestión de Equipos**: Registro y seguimiento de equipos móviles y activos.
- **Órdenes de Trabajo**: Creación, asignación y seguimiento de órdenes de trabajo de mantenimiento.
- **Planes de Mantenimiento**: Programación y gestión de mantenimientos preventivos y predictivos.
- **Checklists**: Implementación de checklists dinámicos para inspecciones y verificaciones.
- **Dashboard Interactivo**: Visualización de KPIs y estadísticas en tiempo real.
- **Módulos de Usuario y Roles**: Gestión de usuarios y permisos.

## 🛠️ Tecnologías Utilizadas

El sistema está compuesto por un backend desarrollado en Django (Python) y un frontend construido con React (TypeScript).

### Backend
- **Lenguaje**: Python 3.11+
- **Framework**: Django
- **Base de Datos**: SQLite (por defecto), MySQL (opcional)
- **Librerías Clave**: Django REST Framework, djangorestframework-simplejwt, Pillow, etc.

### Frontend
- **Lenguaje**: TypeScript
- **Framework**: React 18
- **Build Tool**: Vite
- **Estilos**: Tailwind CSS
- **Gráficos**: Recharts
- **Cliente HTTP**: Axios
- **Navegación**: React Router




## ⚙️ Instalación y Despliegue

Para poner en marcha el sistema CMMS Somacor, sigue los siguientes pasos:

### Prerrequisitos
- **Node.js** 18+
- **Python** 3.11+
- **Git**
- **Base de datos** (SQLite incluida por defecto, MySQL opcional)

### 1. Clonar el Repositorio
```bash
git clone https://github.com/fjparrah/Somacor-CMMS.git
cd Somacor-CMMS/somacor_cmms
```

### 2. Configuración del Backend

#### Instalar Dependencias
```bash
cd backend
pip install -r requirements.txt
```

#### Configurar Base de Datos
```bash
# Aplicar migraciones
python manage.py migrate

# Cargar datos iniciales
python manage.py seed_data

# Crear superusuario (opcional)
python manage.py createsuperuser
```

#### Iniciar Servidor Backend
```bash
python manage.py runserver 0.0.0.0:8000
```

### 3. Configuración del Frontend

#### Instalar Dependencias
```bash
cd ../frontend
npm install
```

#### Configurar Variables de Entorno
```bash
# Crear archivo .env
echo "VITE_API_BASE_URL=http://localhost:8000/api/" > .env
```

#### Iniciar Servidor Frontend
```bash
npm run dev
```

## 🌐 Acceso a la Aplicación

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/
- **Admin Django**: http://localhost:8000/admin/

### Credenciales por Defecto
- **Usuario**: admin
- **Contraseña**: admin123

## 📦 Despliegue en Producción

### Backend (Django)

#### 1. Configurar Variables de Entorno
```bash
# Crear archivo .env en backend/
DEBUG=False
SECRET_KEY=tu_clave_secreta_aqui
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DATABASE_URL=mysql://usuario:password@host:puerto/database
```

#### 2. Configurar Base de Datos de Producción
```bash
# Para MySQL
pip install mysqlclient
python manage.py migrate
python manage.py seed_data
```

#### 3. Recopilar Archivos Estáticos
```bash
python manage.py collectstatic --noinput
```

#### 4. Configurar Servidor Web (Nginx + Gunicorn)
```nginx
# /etc/nginx/sites-available/cmms-somacor
server {
    listen 80;
    server_name tu-dominio.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/your/static/files/;
    }

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

#### 5. Iniciar con Gunicorn
```bash
gunicorn cmms_project.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

### Frontend (React)

#### 1. Configurar Variables de Producción
```bash
# .env.production
VITE_API_BASE_URL=https://tu-dominio.com/api/
```

#### 2. Build de Producción
```bash
npm run build
```

#### 3. Servir Archivos Estáticos
Los archivos generados en `dist/` pueden ser servidos por cualquier servidor web (Nginx, Apache, etc.)

## 🐳 Despliegue con Docker

Se incluyen Dockerfiles y un archivo `docker-compose.yaml` para facilitar el despliegue de la aplicación utilizando contenedores Docker.

### Dockerfile Backend
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "cmms_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Dockerfile Frontend
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
```

### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=sqlite:///db.sqlite3
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: cmms_db
      MYSQL_USER: cmms_user
      MYSQL_PASSWORD: cmms_password
      MYSQL_ROOT_PASSWORD: root_password
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```



## 🔧 Configuración Avanzada

### Configuración de CORS
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://tu-dominio.com",
]
```

### Configuración de Logging
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'cmms.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Configuración de Caché
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```



## 📊 Monitoreo y Mantenimiento

### Comandos de Gestión Útiles
```bash
# Generar agenda de mantenimiento
python manage.py generar_agenda_preventiva

# Procesar mantenimientos vencidos
python manage.py procesar_mantenimientos

# Crear plantillas de checklist
python manage.py crear_plantillas_checklist

# Backup de base de datos
python manage.py dumpdata > backup.json

# Restaurar backup
python manage.py loaddata backup.json
```

### Logs y Debugging
```bash
# Ver logs en tiempo real
tail -f cmms.log

# Verificar estado del sistema
python manage.py check

# Verificar configuración
python manage.py check --deploy
```

## 🔒 Seguridad

### Configuraciones Recomendadas
```python
# settings.py para producción
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Backup Automático
```bash
# Crontab para backup diario
0 2 * * * cd /path/to/project && python manage.py dumpdata > backups/backup_$(date +\%Y\%m\%d).json
```



## 🆘 Solución de Problemas

### Problemas Comunes

#### Error de CORS
```bash
# Verificar configuración CORS en settings.py
# Asegurar que el frontend URL esté en CORS_ALLOWED_ORIGINS
```

#### Error de Base de Datos
```bash
# Verificar conexión
python manage.py dbshell

# Recrear migraciones si es necesario
python manage.py makemigrations --empty app_name
```

#### Error de Dependencias Frontend
```bash
# Limpiar caché y reinstalar
rm -rf node_modules package-lock.json
npm install
```

### Contacto de Soporte
Para problemas técnicos o consultas sobre el sistema, contactar al equipo de desarrollo.

---

## ✅ Checklist de Despliegue

- [ ] Backend configurado y funcionando
- [ ] Frontend compilado y servido
- [ ] Base de datos migrada y con datos iniciales
- [ ] Variables de entorno configuradas
- [ ] CORS configurado correctamente
- [ ] Servidor web configurado (Nginx/Apache)
- [ ] SSL/HTTPS configurado (recomendado)
- [ ] Backup automático configurado
- [ ] Monitoreo y logs configurados
- [ ] Pruebas de funcionalidad completadas

¡El sistema CMMS Somacor está listo para producción! 🎉


