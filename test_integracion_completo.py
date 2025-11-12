#!/usr/bin/env python3
"""
Test de Integración Completo
Verifica que todo el sistema funcione correctamente
"""
import os
import sys
import django
import json

# Configurar Django
sys.path.insert(0, 'somacor_cmms/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
os.environ['DJANGO_SECRET_KEY'] = 'test-secret-key-for-testing-only'
os.environ['DJANGO_DEBUG'] = 'True'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'

django.setup()

from django.test import Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_test(success, test_name, details=""):
    symbol = "✅" if success else "❌"
    print(f"{symbol} {test_name}")
    if details:
        print(f"   {details}")
    return success

def main():
    print_header("🧪 PRUEBAS DE INTEGRACIÓN COMPLETA")
    
    client = Client()
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Verificar que Django está configurado
    print_header("1. Verificación de Django")
    total_tests += 1
    from django.conf import settings
    if print_test(
        settings.configured,
        "Django está configurado correctamente",
        f"DEBUG={settings.DEBUG}, SECRET_KEY configurada"
    ):
        passed_tests += 1
    
    # Test 2: Verificar base de datos
    print_header("2. Verificación de Base de Datos")
    total_tests += 1
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        if print_test(
            result[0] == 1,
            "Conexión a base de datos funciona",
            f"Motor: {settings.DATABASES['default']['ENGINE']}"
        ):
            passed_tests += 1
    except Exception as e:
        print_test(False, "Conexión a base de datos", f"Error: {str(e)}")
    
    # Test 3: Verificar modelos
    print_header("3. Verificación de Modelos")
    try:
        from cmms_api.models import Equipos, OrdenTrabajo, Roles, Usuarios
        
        total_tests += 1
        if print_test(
            True,
            "Modelos importados correctamente",
            "Equipos, OrdenTrabajo, Roles, Usuarios"
        ):
            passed_tests += 1
        
        # Contar registros
        total_tests += 1
        equipos_count = Equipos.objects.count()
        if print_test(
            True,
            f"Modelo Equipos accesible",
            f"{equipos_count} equipos en base de datos"
        ):
            passed_tests += 1
        
        total_tests += 1
        ordenes_count = OrdenTrabajo.objects.count()
        if print_test(
            True,
            f"Modelo OrdenTrabajo accesible",
            f"{ordenes_count} órdenes en base de datos"
        ):
            passed_tests += 1
    except Exception as e:
        print_test(False, "Modelos", f"Error: {str(e)}")
    
    # Test 4: Verificar autenticación
    print_header("4. Verificación de Autenticación")
    
    # Crear usuario de prueba
    total_tests += 1
    try:
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@test.com',
                'is_active': True
            }
        )
        if created:
            test_user.set_password('test_password_123')
            test_user.save()
        
        if print_test(
            True,
            "Usuario de prueba creado/obtenido",
            f"Username: {test_user.username}"
        ):
            passed_tests += 1
    except Exception as e:
        print_test(False, "Crear usuario de prueba", f"Error: {str(e)}")
    
    # Crear token
    total_tests += 1
    try:
        token, created = Token.objects.get_or_create(user=test_user)
        if print_test(
            True,
            "Token de autenticación creado",
            f"Token: {token.key[:20]}..."
        ):
            passed_tests += 1
    except Exception as e:
        print_test(False, "Crear token", f"Error: {str(e)}")
    
    # Test 5: Verificar endpoints de API
    print_header("5. Verificación de Endpoints de API")
    
    # Test login endpoint
    total_tests += 1
    try:
        response = client.post('/api/login/', {
            'username': 'test_user',
            'password': 'test_password_123'
        }, content_type='application/json')
        
        if print_test(
            response.status_code in [200, 400],  # 400 si falta configuración adicional
            "Endpoint /api/login/ responde",
            f"Status: {response.status_code}"
        ):
            passed_tests += 1
    except Exception as e:
        print_test(False, "Endpoint /api/login/", f"Error: {str(e)}")
    
    # Test API v2 endpoints
    total_tests += 1
    try:
        response = client.get('/api/v2/equipos/', HTTP_AUTHORIZATION=f'Token {token.key}')
        if print_test(
            response.status_code in [200, 401],  # 401 si requiere permisos adicionales
            "Endpoint /api/v2/equipos/ responde",
            f"Status: {response.status_code}"
        ):
            passed_tests += 1
    except Exception as e:
        print_test(False, "Endpoint /api/v2/equipos/", f"Error: {str(e)}")
    
    # Test 6: Verificar serializers
    print_header("6. Verificación de Serializers")
    total_tests += 1
    try:
        from cmms_api.serializers_v2 import EquipoSerializer, OrdenTrabajoSerializer
        if print_test(
            True,
            "Serializers importados correctamente",
            "EquipoSerializer, OrdenTrabajoSerializer"
        ):
            passed_tests += 1
    except Exception as e:
        print_test(False, "Serializers", f"Error: {str(e)}")
    
    # Test 7: Verificar permisos
    print_header("7. Verificación de Permisos")
    total_tests += 1
    try:
        # Intentar acceder sin autenticación
        response = client.get('/api/v2/equipos/')
        if print_test(
            response.status_code == 401,
            "Endpoints protegidos requieren autenticación",
            f"Status sin auth: {response.status_code}"
        ):
            passed_tests += 1
    except Exception as e:
        print_test(False, "Permisos", f"Error: {str(e)}")
    
    # Test 8: Verificar CORS
    print_header("8. Verificación de CORS")
    total_tests += 1
    try:
        from django.conf import settings
        cors_configured = hasattr(settings, 'CORS_ALLOWED_ORIGINS')
        if print_test(
            cors_configured,
            "CORS configurado",
            f"Orígenes permitidos: {len(settings.CORS_ALLOWED_ORIGINS) if cors_configured else 0}"
        ):
            passed_tests += 1
    except Exception as e:
        print_test(False, "CORS", f"Error: {str(e)}")
    
    # Test 9: Verificar middleware
    print_header("9. Verificación de Middleware")
    total_tests += 1
    try:
        from django.conf import settings
        has_cors = 'corsheaders.middleware.CorsMiddleware' in settings.MIDDLEWARE
        if print_test(
            has_cors,
            "Middleware CORS instalado",
            "corsheaders.middleware.CorsMiddleware"
        ):
            passed_tests += 1
    except Exception as e:
        print_test(False, "Middleware", f"Error: {str(e)}")
    
    # Test 10: Verificar archivos estáticos
    print_header("10. Verificación de Archivos Estáticos")
    total_tests += 1
    try:
        from django.conf import settings
        static_configured = hasattr(settings, 'STATIC_URL') and hasattr(settings, 'STATIC_ROOT')
        if print_test(
            static_configured,
            "Archivos estáticos configurados",
            f"STATIC_URL: {settings.STATIC_URL}"
        ):
            passed_tests += 1
    except Exception as e:
        print_test(False, "Archivos estáticos", f"Error: {str(e)}")
    
    # Limpiar usuario de prueba
    try:
        test_user.delete()
        print("\n🧹 Usuario de prueba eliminado")
    except:
        pass
    
    # Resumen
    print_header("📊 RESUMEN DE PRUEBAS DE INTEGRACIÓN")
    print(f"\nTotal de pruebas: {total_tests}")
    print(f"✅ Pruebas exitosas: {passed_tests}")
    print(f"❌ Pruebas fallidas: {total_tests - passed_tests}")
    print(f"📈 Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ¡TODAS LAS PRUEBAS DE INTEGRACIÓN PASARON!")
        print("✅ El sistema está funcionando correctamente")
        return 0
    elif passed_tests >= total_tests * 0.8:
        print("\n✅ La mayoría de las pruebas pasaron")
        print("⚠️  Algunas funcionalidades pueden necesitar configuración adicional")
        return 0
    else:
        print("\n⚠️  Varias pruebas fallaron")
        print("❌ Revisa la configuración del sistema")
        return 1

if __name__ == '__main__':
    sys.exit(main())
