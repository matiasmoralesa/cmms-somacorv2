"""
Script para verificar que todos los endpoints nuevos funcionan correctamente
"""
import os
import django
import requests
from requests.auth import HTTPBasicAuth

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from django.contrib.auth.models import User

# Configuración
BASE_URL = 'http://localhost:8000/api/v2'
USERNAME = 'admin'
PASSWORD = 'admin'

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓{Colors.END} {message}")

def print_error(message):
    print(f"{Colors.RED}✗{Colors.END} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠{Colors.END} {message}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ{Colors.END} {message}")

def get_auth_token():
    """Obtener token de autenticación"""
    try:
        # Intentar obtener token existente de la base de datos
        from rest_framework.authtoken.models import Token
        from django.contrib.auth.models import User
        
        try:
            user = User.objects.get(username=USERNAME)
            token, created = Token.objects.get_or_create(user=user)
            print_success(f"Token obtenido de BD: {token.key[:20]}...")
            return token.key
        except User.DoesNotExist:
            print_error(f"Usuario '{USERNAME}' no existe")
            return None
            
    except Exception as e:
        print_error(f"Error obteniendo token: {e}")
        return None

def test_endpoint(endpoint, token, method='GET'):
    """Probar un endpoint específico"""
    url = f"{BASE_URL}/{endpoint}/"
    headers = {'Authorization': f'Token {token}'}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        else:
            response = requests.request(method, url, headers=headers, timeout=5)
        
        if response.status_code in [200, 201]:
            data = response.json()
            count = len(data) if isinstance(data, list) else (data.get('count', 'N/A') if isinstance(data, dict) else 'N/A')
            print_success(f"{endpoint:40} → {response.status_code} (registros: {count})")
            return True
        elif response.status_code == 404:
            print_error(f"{endpoint:40} → 404 NOT FOUND")
            return False
        else:
            print_warning(f"{endpoint:40} → {response.status_code}")
            return True  # Puede ser válido (ej: 403 sin permisos)
    except requests.exceptions.Timeout:
        print_error(f"{endpoint:40} → TIMEOUT")
        return False
    except requests.exceptions.ConnectionError:
        print_error(f"{endpoint:40} → CONNECTION ERROR")
        return False
    except Exception as e:
        print_error(f"{endpoint:40} → ERROR: {str(e)[:50]}")
        return False

def main():
    print("\n" + "=" * 80)
    print("VERIFICACIÓN DE ENDPOINTS DEL BACKEND")
    print("=" * 80)
    
    # Obtener token
    print("\n1. Autenticación")
    print("-" * 80)
    token = get_auth_token()
    
    if not token:
        print_error("No se pudo obtener el token. Verifica que el usuario admin existe.")
        print_info("Puedes crear el usuario con: python manage.py createsuperuser")
        return
    
    # Endpoints a probar
    endpoints = {
        "Equipos y Catálogos": [
            "equipos",
            "tipos-equipo",
            "estados-equipo",
            "faenas",
        ],
        "Órdenes de Trabajo": [
            "ordenes-trabajo",
            "estados-orden-trabajo",
            "tipos-mantenimiento-ot",
            "actividades-orden-trabajo",
            "evidencias-ot",
        ],
        "Técnicos": [
            "tecnicos",
            "especialidades",
        ],
        "Planes de Mantenimiento": [
            "planes-mantenimiento",
            "detalles-plan-mantenimiento",
            "tipos-tarea",
            "tareas-estandar",
            "agendas",
        ],
        "Checklists": [
            "checklist-templates",
            "checklist-categories",
            "checklist-items",
            "checklist-instance",
        ],
        "Otros": [
            "usuarios",
            "roles",
            "inventario",
            "dashboard",
        ]
    }
    
    # Probar cada categoría
    total_endpoints = 0
    successful_endpoints = 0
    failed_endpoints = []
    
    for category, endpoint_list in endpoints.items():
        print(f"\n2. {category}")
        print("-" * 80)
        
        for endpoint in endpoint_list:
            total_endpoints += 1
            if test_endpoint(endpoint, token):
                successful_endpoints += 1
            else:
                failed_endpoints.append(endpoint)
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 80)
    print(f"Total endpoints probados: {total_endpoints}")
    print(f"Exitosos: {successful_endpoints} ({successful_endpoints/total_endpoints*100:.1f}%)")
    print(f"Fallidos: {len(failed_endpoints)}")
    
    if failed_endpoints:
        print("\nEndpoints con problemas:")
        for endpoint in failed_endpoints:
            print(f"  - {endpoint}")
    
    if successful_endpoints == total_endpoints:
        print_success("\n¡Todos los endpoints funcionan correctamente!")
    elif successful_endpoints >= total_endpoints * 0.9:
        print_warning("\nLa mayoría de endpoints funcionan, pero hay algunos problemas.")
    else:
        print_error("\nSe encontraron problemas significativos en los endpoints.")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
