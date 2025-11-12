#!/usr/bin/env python3
"""
Test de Health Checks
Verifica que los endpoints de health check funcionen correctamente
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, 'somacor_cmms/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
os.environ['DJANGO_SECRET_KEY'] = 'test-secret-key-for-testing-only'
os.environ['DJANGO_DEBUG'] = 'True'  # Para testing
os.environ['DJANGO_ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'  # Agregar testserver

django.setup()

from django.test import Client
from django.urls import reverse
import json

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def test_endpoint(client, url, expected_status, test_name):
    try:
        response = client.get(url)
        
        if response.status_code == expected_status:
            print(f"✅ {test_name}")
            print(f"   URL: {url}")
            print(f"   Status: {response.status_code}")
            
            # Intentar parsear JSON
            try:
                data = json.loads(response.content)
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"   Response: {response.content[:100]}...")
            
            return True, response
        else:
            print(f"❌ {test_name}")
            print(f"   URL: {url}")
            print(f"   Esperado: {expected_status}")
            print(f"   Actual: {response.status_code}")
            print(f"   Response: {response.content[:200]}")
            return False, response
    except Exception as e:
        print(f"❌ {test_name}")
        print(f"   Error: {str(e)}")
        return False, None

def main():
    print_header("🧪 PRUEBAS DE HEALTH CHECKS")
    
    client = Client()
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Health Check Principal
    print_header("1. Health Check Principal (/health/)")
    total_tests += 1
    success, response = test_endpoint(
        client,
        '/health/',
        200,
        "Endpoint /health/ responde correctamente"
    )
    if success:
        passed_tests += 1
        # Verificar estructura de respuesta
        try:
            data = json.loads(response.content)
            if 'status' in data and 'checks' in data:
                print("   ✅ Estructura de respuesta correcta")
                print(f"   Status: {data.get('status')}")
                print(f"   Checks: {list(data.get('checks', {}).keys())}")
            else:
                print("   ⚠️  Estructura de respuesta incompleta")
        except:
            pass
    
    # Test 2: Readiness Check
    print_header("2. Readiness Check (/health/ready/)")
    total_tests += 1
    success, response = test_endpoint(
        client,
        '/health/ready/',
        200,
        "Endpoint /health/ready/ responde correctamente"
    )
    if success:
        passed_tests += 1
    
    # Test 3: Liveness Check
    print_header("3. Liveness Check (/health/live/)")
    total_tests += 1
    success, response = test_endpoint(
        client,
        '/health/live/',
        200,
        "Endpoint /health/live/ responde correctamente"
    )
    if success:
        passed_tests += 1
    
    # Test 4: API Test Endpoint
    print_header("4. API Test Endpoint (/api/test/)")
    total_tests += 1
    success, response = test_endpoint(
        client,
        '/api/test/',
        200,
        "Endpoint /api/test/ responde correctamente"
    )
    if success:
        passed_tests += 1
    
    # Test 5: Admin Panel (debe existir)
    print_header("5. Admin Panel (/admin/)")
    total_tests += 1
    success, response = test_endpoint(
        client,
        '/admin/',
        200,  # Puede ser 200 o 302 (redirect a login)
        "Admin panel accesible"
    )
    # Admin puede redirigir, así que aceptamos 200 o 302
    if success or (response and response.status_code == 302):
        passed_tests += 1
        print("   ✅ Admin panel accesible (puede requerir login)")
    
    # Resumen
    print_header("📊 RESUMEN DE PRUEBAS DE HEALTH CHECKS")
    print(f"\nTotal de pruebas: {total_tests}")
    print(f"✅ Pruebas exitosas: {passed_tests}")
    print(f"❌ Pruebas fallidas: {total_tests - passed_tests}")
    print(f"📈 Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ¡TODOS LOS HEALTH CHECKS FUNCIONAN!")
        print("✅ Los endpoints de monitoreo están operativos")
        return 0
    else:
        print("\n⚠️  Algunos health checks necesitan revisión")
        return 1

if __name__ == '__main__':
    sys.exit(main())
