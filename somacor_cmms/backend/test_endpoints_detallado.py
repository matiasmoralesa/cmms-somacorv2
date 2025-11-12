"""
Script para probar endpoints con errores y ver detalles
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

def test_endpoints_con_errores():
    """Probar endpoints que dieron error 500"""
    
    # Crear cliente de prueba
    client = APIClient()
    
    # Obtener token
    user = User.objects.first()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    
    print("=" * 80)
    print("PRUEBA DETALLADA DE ENDPOINTS CON ERRORES")
    print("=" * 80)
    
    endpoints_con_error = [
        '/api/v2/actividades-orden-trabajo/',
        '/api/v2/evidencias-ot/',
        '/api/v2/planes-mantenimiento/',
        '/api/v2/detalles-plan-mantenimiento/',
        '/api/v2/tareas-estandar/',
        '/api/v2/agendas/',
    ]
    
    for endpoint in endpoints_con_error:
        print(f"\n{endpoint}")
        print("-" * 80)
        try:
            response = client.get(endpoint)
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                print(f"Error: {response.data if hasattr(response, 'data') else response.content}")
        except Exception as e:
            print(f"Exception: {type(e).__name__}: {str(e)}")

if __name__ == '__main__':
    test_endpoints_con_errores()
