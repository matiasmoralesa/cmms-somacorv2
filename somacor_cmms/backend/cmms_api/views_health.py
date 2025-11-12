"""
Health Check Views para monitoreo del sistema
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import time
import sys


@api_view(['GET'])
@permission_classes([AllowAny])  # Health check debe ser público
def health_check(request):
    """
    Endpoint de health check para monitoreo del sistema.
    Verifica el estado de componentes críticos.
    """
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'version': settings.CMMS_API.get('VERSION', '1.0.0'),
        'environment': 'production' if not settings.DEBUG else 'development',
        'checks': {}
    }
    
    # Check de base de datos
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection OK'
        }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database error: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Check de cache
    try:
        cache_key = 'health_check_test'
        cache.set(cache_key, 'ok', 30)
        cache_value = cache.get(cache_key)
        if cache_value == 'ok':
            health_status['checks']['cache'] = {
                'status': 'healthy',
                'message': 'Cache working OK'
            }
        else:
            health_status['checks']['cache'] = {
                'status': 'warning',
                'message': 'Cache not working as expected'
            }
    except Exception as e:
        health_status['checks']['cache'] = {
            'status': 'warning',
            'message': f'Cache error: {str(e)}'
        }
    
    # Check de espacio en disco
    try:
        import shutil
        total, used, free = shutil.disk_usage('/')
        free_percent = (free / total) * 100
        
        if free_percent > 10:
            health_status['checks']['disk_space'] = {
                'status': 'healthy',
                'message': f'{free_percent:.1f}% free',
                'free_gb': round(free / (1024**3), 2)
            }
        elif free_percent > 5:
            health_status['checks']['disk_space'] = {
                'status': 'warning',
                'message': f'Low disk space: {free_percent:.1f}% free',
                'free_gb': round(free / (1024**3), 2)
            }
        else:
            health_status['checks']['disk_space'] = {
                'status': 'critical',
                'message': f'Critical disk space: {free_percent:.1f}% free',
                'free_gb': round(free / (1024**3), 2)
            }
            health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['disk_space'] = {
            'status': 'unknown',
            'message': f'Could not check disk space: {str(e)}'
        }
    
    # Check de memoria (opcional, requiere psutil)
    try:
        import psutil
        memory = psutil.virtual_memory()
        
        if memory.percent < 85:
            health_status['checks']['memory'] = {
                'status': 'healthy',
                'message': f'{memory.percent:.1f}% used',
                'available_gb': round(memory.available / (1024**3), 2)
            }
        elif memory.percent < 95:
            health_status['checks']['memory'] = {
                'status': 'warning',
                'message': f'High memory usage: {memory.percent:.1f}%',
                'available_gb': round(memory.available / (1024**3), 2)
            }
        else:
            health_status['checks']['memory'] = {
                'status': 'critical',
                'message': f'Critical memory usage: {memory.percent:.1f}%',
                'available_gb': round(memory.available / (1024**3), 2)
            }
            health_status['status'] = 'unhealthy'
    except ImportError:
        health_status['checks']['memory'] = {
            'status': 'unknown',
            'message': 'psutil not installed'
        }
    except Exception as e:
        health_status['checks']['memory'] = {
            'status': 'unknown',
            'message': f'Could not check memory: {str(e)}'
        }
    
    # Información del sistema
    health_status['system_info'] = {
        'python_version': sys.version.split()[0],
        'debug_mode': settings.DEBUG,
    }
    
    # Determinar código de respuesta HTTP
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Endpoint de readiness para Kubernetes/Docker.
    Verifica si la aplicación está lista para recibir tráfico.
    """
    try:
        # Verificar conexión a base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return JsonResponse({
            'status': 'ready',
            'timestamp': time.time()
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': time.time()
        }, status=503)


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check(request):
    """
    Endpoint de liveness para Kubernetes/Docker.
    Verifica si la aplicación está viva (no bloqueada).
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': time.time()
    }, status=200)
