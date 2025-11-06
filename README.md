# 🚀 CMMS Somacor v2 - Sistema Completo de Gestión de Mantenimiento

**Estado**: ✅ **100% OPERATIVO**  
**Última actualización**: Noviembre 2025  
**Repositorio**: https://github.com/matiasmoralesa/cmms-somacorv2

Este repositorio contiene el código fuente completo del Sistema de Gestión de Mantenimiento Computarizado (CMMS) desarrollado para Somacor. Es un **sistema distribuido avanzado** que integra inteligencia artificial, automatización y múltiples interfaces para optimizar la gestión de mantenimiento industrial.

## 🎯 Arquitectura del Sistema

### Componentes Principales

| Componente | Puerto | Estado | Descripción |
|------------|--------|--------|-------------|
| **Backend Django** | 8000 | ✅ Activo | API REST + WebSockets |
| **Frontend React** | 5173/5174 | ✅ Activo | SPA con TypeScript |
| **Bot Telegram** | - | ✅ Activo | @Somacorbot con roles |
| **Apache Airflow** | 8080 | ✅ Activo | Orquestación de flujos |
| **Dask Cluster** | 8786-8787 | ✅ Activo | Procesamiento distribuido |

### 🚀 Características Avanzadas

- **🤖 Inteligencia Artificial**: Predicción de fallas con Machine Learning
- **⚡ Automatización**: 3 DAGs de Airflow para procesos automáticos
- **📱 Bot Telegram**: Sistema de roles con 15+ comandos interactivos
- **📊 Análisis Predictivo**: Procesamiento distribuido con Dask
- **🔄 Tiempo Real**: WebSockets para notificaciones instantáneas
- **📈 Dashboard Avanzado**: KPIs y métricas en tiempo real
- **🛠️ Gestión Completa**: Equipos, OT, planes, checklists, inventario

## 🛠️ Stack Tecnológico

### Backend (Django)
```python
Django==4.2.23                    # Framework web
djangorestframework==3.16.0       # API REST
channels                          # WebSockets
pandas, numpy                     # Análisis de datos
matplotlib, plotly                # Visualizaciones
```

### Frontend (React + TypeScript)
```json
{
  "react": "^19.1.0",             // Framework UI
  "typescript": "latest",          // Tipado estático
  "vite": "latest",               // Build tool
  "tailwindcss": "latest",        // CSS framework
  "@radix-ui/*": "latest",        // Componentes UI
  "recharts": "^2.15.3",          // Gráficos
  "axios": "^1.9.0"               // Cliente HTTP
}
```

### Infraestructura y AI
- **Apache Airflow**: Orquestación de flujos de trabajo
- **Dask**: Computación distribuida y paralela
- **Machine Learning**: Scikit-learn, pandas para predicción
- **Telegram Bot API**: Interfaz conversacional
- **SQLite/PostgreSQL**: Base de datos




## 📊 Capacidades y Rendimiento

### Datos del Sistema
- **200 equipos** registrados y monitoreados
- **1,050+ órdenes de trabajo** gestionadas
- **Múltiples faenas** y ubicaciones
- **Checklists dinámicos** con templates
- **Inventario completo** de repuestos

### Rendimiento Comprobado
| Métrica | Resultado |
|---------|-----------|
| Procesamiento API | **347,642 equipos/seg** |
| Análisis Dask | **52,500 registros/seg** |
| Predicción ML | **1,724 equipos/seg** |
| Bot Telegram | **< 1 segundo** respuesta |
| Frontend | **< 2 segundos** carga inicial |

### Automatización Inteligente
- **Predicción de fallas** antes de que ocurran
- **Mantenimiento preventivo** programado automáticamente
- **Procesamiento de checklists** con detección de anomalías
- **Asignación automática** de técnicos
- **Reportes automáticos** diarios, semanales y mensuales

## ⚙️ Instalación y Despliegue

### 🚀 Inicio Rápido (5 minutos)

**Prerrequisitos**:
- Python 3.11+
- Node.js 18+
- Git

**Instalación automática**:

```bash
# 1. Clonar repositorio
git clone https://github.com/matiasmoralesa/cmms-somacorv2.git
cd cmms-somacorv2

# 2. Instalar y configurar todo automáticamente
cd airflow_bot
chmod +x setup.sh
./setup.sh

# 3. Iniciar todos los servicios
cd ..
./start_all.sh
```

**¡Listo!** El sistema estará disponible en:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Airflow**: http://localhost:8080 (admin/admin123)
- **Dask Dashboard**: http://localhost:8787
- **Bot Telegram**: @Somacorbot

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

## 🤖 Bot de Telegram (@Somacorbot)

### Sistema de Roles
| Rol | Icono | Permisos |
|-----|-------|----------|
| **Administrador** | 👑 | Acceso total + gestión de usuarios |
| **Supervisor** | 👔 | Gestión de órdenes y reportes |
| **Técnico** | 🔧 | Órdenes de trabajo asignadas |
| **Operador** | 👷 | Monitoreo de equipos y alertas |
| **Invitado** | 👤 | Comandos básicos |

### Comandos Principales
```
/start       - Iniciar bot
/help        - Ver comandos disponibles
/status      - Estado del sistema
/equipos     - Lista de equipos
/ordenes     - Órdenes de trabajo
/pendientes  - Órdenes pendientes
/alertas     - Alertas predictivas
/kpis        - KPIs del sistema
```

## 🌐 URLs de Acceso

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Frontend** | http://localhost:5173 | - |
| **Backend API** | http://localhost:8000/api/ | - |
| **Airflow** | http://localhost:8080 | admin/admin123 |
| **Dask Dashboard** | http://localhost:8787 | - |
| **Admin Django** | http://localhost:8000/admin/ | Crear superusuario |

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

## 📚 Documentación Completa

- **[Guía de Inicio Rápido](GUIA_INICIO_RAPIDO.md)** - Instalación en 10 minutos
- **[Documentación del Bot](GUIA_BOT_TELEGRAM.md)** - Comandos y roles
- **[Sistema Airflow + Dask](SISTEMA_COMPLETO_AIRFLOW_DASK.md)** - Arquitectura completa
- **[Estado Final](ESTADO_FINAL_SISTEMA_COMPLETO.md)** - Resumen del proyecto
- **[Reporte de Rendimiento](REPORTE_PRUEBAS_RENDIMIENTO.md)** - Métricas y pruebas

## 🎯 Casos de Uso

1. **🔮 Mantenimiento Predictivo**: Predice fallas antes de que ocurran
2. **⚡ Automatización Total**: Crea órdenes automáticamente
3. **📱 Gestión Móvil**: Bot de Telegram para técnicos en campo
4. **📊 Análisis Avanzado**: Dashboard con KPIs en tiempo real
5. **🔄 Integración Completa**: API REST para sistemas externos

## 🏆 Ventajas Competitivas

- **Arquitectura Moderna**: Microservicios distribuidos
- **Escalabilidad**: Dask permite procesamiento masivo
- **Inteligencia Artificial**: ML integrado para predicciones
- **Múltiples Interfaces**: Web, Telegram, API
- **Tiempo Real**: WebSockets para actualizaciones instantáneas
- **Documentación Completa**: Guías paso a paso

## 🆘 Soporte

- **Repositorio**: https://github.com/matiasmoralesa/cmms-somacorv2
- **Bot Telegram**: @Somacorbot
- **Issues**: GitHub Issues para reportar problemas

---

**¡El sistema CMMS Somacor v2 está 100% operativo y listo para producción!** 🚀

*Desarrollado con ❤️ para optimizar el mantenimiento industrial*


