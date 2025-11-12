# CMMS Somacor v2

Sistema completo de gestión de mantenimiento (CMMS) para Somacor.

> 📚 **Documentación Completa:** Ver [DOCUMENTACION_COMPLETA_PROYECTO.md](./DOCUMENTACION_COMPLETA_PROYECTO.md) para información detallada sobre optimizaciones, implementación y guías de uso.

## 🚀 Características

- **Backend Django REST Framework**: API robusta con autenticación JWT
- **Frontend React + TypeScript**: Interfaz moderna y responsiva
- **WebSockets**: Actualizaciones en tiempo real
- **Gestión de Órdenes de Trabajo**: Sistema completo de OT
- **Planes de Mantenimiento**: Configuración y seguimiento de planes
- **Checklists**: Sistema de checklists para mantenimiento
- **Inventario**: Gestión de inventario y equipos
- **Técnicos**: Gestión de técnicos y perfiles
- **Faenas**: Gestión de faenas y equipos móviles

## 📋 Requisitos

### Backend
- Python 3.12+
- Django 4.2+
- PostgreSQL (recomendado) o SQLite

### Frontend
- Node.js 18+
- npm o yarn

## 🔧 Instalación

### Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🌐 URLs

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/api/docs/

## 📝 Uso

1. Inicia el backend: `python manage.py runserver`
2. Inicia el frontend: `npm run dev`
3. Accede a http://localhost:5173
4. Inicia sesión con tus credenciales

## 🛠️ Tecnologías

- **Backend**: Django, Django REST Framework, Channels (WebSockets)
- **Frontend**: React, TypeScript, Tailwind CSS, Shadcn/ui
- **Base de datos**: PostgreSQL / SQLite
- **Autenticación**: JWT (JSON Web Tokens)

## 📦 Estructura del Proyecto

```
somacor_cmms/
├── backend/              # Backend Django
│   ├── cmms_api/        # Aplicación principal
│   ├── cmms_project/    # Configuración del proyecto
│   └── manage.py
├── frontend/            # Frontend React
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   ├── pages/      # Páginas/Views
│   │   ├── services/   # Servicios API
│   │   └── hooks/      # Custom hooks
│   └── package.json
└── README.md
```

## 🔐 Autenticación

El sistema usa autenticación JWT. Para obtener un token:

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "tu_usuario", "password": "tu_contraseña"}'
```

## 📄 Licencia

Este proyecto es propiedad de Somacor.

## 👥 Contribuidores

- Equipo de Desarrollo Somacor

## 📞 Soporte

Para soporte, contacta al equipo de desarrollo.

