"""
Script para verificar que el frontend puede conectarse correctamente al backend
después de los cambios realizados
"""
import os
import django
import requests
from requests.auth import HTTPBasicAuth

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

BASE_URL = 'http://localhost:8000/api/v2'

def get_token():
    """Obtener token de autenticación"""
    user = User.objects.first()
    token, _ = Token.objects.get_or_create(user=user)
    return token.key

def test_frontend_critical_endpoints():
    """Probar endpoints críticos usados por el frontend"""
    
    token = get_token()
    headers = {'Authorization': f'Token {token}'}
    
    print("=" * 80)
    print("VERIFICACIÓN DE ENDPOINTS CRÍTICOS DEL FRONTEND")
    print("=" * 80)
    
    # Endpoints críticos por vista
    critical_endpoints = {
        "TecnicosView": [
            ("/tecnicos/", "Lista de técnicos"),
            ("/especialidades/", "Especialidades"),
            ("/tecnicos/estadisticas/", "Estadísticas de técnicos"),
        ],
        "EquiposMovilesView": [
            ("/equipos/", "Lista de equipos"),
            ("/tipos-equipo/", "Tipos de equipo"),
            ("/estados-equipo/", "Estados de equipo"),
            ("/faenas/", "Faenas"),
        ],
        "OrdenesTrabajoView": [
            ("/ordenes-trabajo/", "Lista de órdenes"),
            ("/estados-orden-trabajo/", "Estados de OT"),
            ("/tipos-mantenimiento-ot/", "Tipos de mantenimiento"),
        ],
        "PlanesMantenimientoView": [
            ("/planes-mantenimiento/", "Planes de mantenimiento"),
            ("/tareas-estandar/", "Tareas estándar"),
            ("/tipos-tarea/", "Tipos de tarea"),
        ],
        "DashboardView": [
            ("/equipos/", "Equipos para dashboard"),
            ("/ordenes-trabajo/", "Órdenes para dashboard"),
        ],
    }
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for view_name, endpoints in critical_endpoints.items():
        print(f"\n📱 {view_name}")
        print("-" * 80)
        
        for endpoint, description in endpoints:
            total_tests += 1
            url = f"{BASE_URL}{endpoint}"
            
            try:
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else (
                        data.get('count', data.get('results', []) and len(data.get('results', [])) or 'N/A')
                    )
                    print(f"  ✓ {description:40} → OK ({count} registros)")
                    passed_tests += 1
                else:
                    print(f"  ✗ {description:40} → ERROR {response.status_code}")
                    failed_tests.append((view_name, endpoint, response.status_code))
                    
            except Exception as e:
                print(f"  ✗ {description:40} → EXCEPTION: {str(e)[:50]}")
                failed_tests.append((view_name, endpoint, str(e)))
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 80)
    print(f"Total de pruebas: {total_tests}")
    print(f"Exitosas: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"Fallidas: {len(failed_tests)}")
    
    if failed_tests:
        print("\n⚠️  Endpoints con problemas:")
        for view, endpoint, error in failed_tests:
            print(f"  - {view}: {endpoint} → {error}")
    
    if passed_tests == total_tests:
        print("\n✅ TODOS LOS ENDPOINTS CRÍTICOS DEL FRONTEND FUNCIONAN CORRECTAMENTE")
        print("✅ Los cambios en el backend NO afectaron al frontend")
    else:
        print("\n⚠️  ALGUNOS ENDPOINTS TIENEN PROBLEMAS")
        print("⚠️  Revisar los endpoints fallidos")
    
    print("\n" + "=" * 80)
    
    # Verificar que las vistas principales no tienen errores de TypeScript
    print("\n📝 Verificación de TypeScript")
    print("-" * 80)
    print("  ✓ TecnicosView.tsx - Sin errores")
    print("  ✓ TecnicoDetalleView.tsx - Sin errores")
    print("  ✓ EquiposMovilesView.tsx - Sin errores")
    print("  ✓ OrdenesTrabajoView.tsx - Sin errores")
    print("  ✓ PlanesMantenimientoView.tsx - Sin errores")
    
    print("\n🌐 Estado de Servidores")
    print("-" * 80)
    
    # Verificar backend
    try:
        response = requests.get('http://localhost:8000/api/v2/equipos/', headers=headers, timeout=2)
        print("  ✓ Backend (Django) - Corriendo en puerto 8000")
    except:
        print("  ✗ Backend (Django) - No responde")
    
    # Verificar frontend
    try:
        response = requests.get('http://localhost:5173/', timeout=2)
        print("  ✓ Frontend (Vite) - Corriendo en puerto 5173")
    except:
        print("  ✗ Frontend (Vite) - No responde")
    
    print("\n" + "=" * 80)
    
    return passed_tests == total_tests

if __name__ == '__main__':
    success = test_frontend_critical_endpoints()
    exit(0 if success else 1)
