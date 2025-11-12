"""
URL configuration for cmms_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# --- INICIO DE LA MODIFICACIÓN ---
from django.conf import settings
from django.conf.urls.static import static
# --- FIN DE LA MODIFICACIÓN ---

from django.http import HttpResponse, JsonResponse
from cmms_api.views_health import health_check, readiness_check, liveness_check

def test_api(request):
    return HttpResponse("API funcionando correctamente")

def websocket_fallback(request, endpoint):
    """Fallback para endpoints de WebSocket que no están disponibles"""
    return JsonResponse({
        'message': f'WebSocket endpoint /ws/{endpoint}/ no disponible',
        'status': 'fallback_mode',
        'note': 'La aplicación funciona sin WebSockets'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/test/', test_api, name='test_api'),
    path('api/', include('cmms_api.urls')),  # APIs principales con V2
    
    # Health check endpoints (públicos para monitoreo)
    path('health/', health_check, name='health_check'),
    path('health/ready/', readiness_check, name='readiness_check'),
    path('health/live/', liveness_check, name='liveness_check'),
    
    # Fallbacks para WebSockets (evitar errores 404)
    path('ws/notifications/', websocket_fallback, {'endpoint': 'notifications'}, name='ws_notifications_fallback'),
    path('ws/dashboard/', websocket_fallback, {'endpoint': 'dashboard'}, name='ws_dashboard_fallback'),
    path('ws/equipos/', websocket_fallback, {'endpoint': 'equipos'}, name='ws_equipos_fallback'),
    path('ws/ordenes/', websocket_fallback, {'endpoint': 'ordenes'}, name='ws_ordenes_fallback'),
]

# --- INICIO DE LA MODIFICACIÓN ---
# Esta configuración permite a Django servir archivos subidos por usuarios (media files)
# durante el desarrollo. En producción, esto se debe manejar con un servidor web como Nginx.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# --- FIN DE LA MODIFICACIÓN ---
