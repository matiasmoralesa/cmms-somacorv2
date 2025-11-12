#!/usr/bin/env python3
"""
Test de Configuración de Seguridad
Verifica que todas las configuraciones de seguridad estén correctas
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, 'somacor_cmms/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')

# Simular ambiente de producción
os.environ['ENVIRONMENT'] = 'development'  # Usar development para testing
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_SECRET_KEY'] = 'test-secret-key-for-testing-only'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'
os.environ['CORS_ALLOW_ALL_ORIGINS'] = 'False'
os.environ['CORS_ALLOWED_ORIGINS'] = 'http://localhost:3000,http://localhost:5173'

django.setup()

from django.conf import settings
from django.test.utils import get_runner

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def test_result(condition, test_name, expected, actual):
    if condition:
        print(f"✅ {test_name}")
        print(f"   Esperado: {expected}")
        print(f"   Actual: {actual}")
        return True
    else:
        print(f"❌ {test_name}")
        print(f"   Esperado: {expected}")
        print(f"   Actual: {actual}")
        return False

def main():
    print_header("🧪 PRUEBAS DE CONFIGURACIÓN DE SEGURIDAD")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    # Test 1: SECRET_KEY
    print_header("1. Verificación de SECRET_KEY")
    total_tests += 1
    if test_result(
        settings.SECRET_KEY == 'test-secret-key-for-testing-only',
        "SECRET_KEY configurada desde variable de entorno",
        "test-secret-key-for-testing-only",
        settings.SECRET_KEY
    ):
        passed_tests += 1
    else:
        failed_tests.append("SECRET_KEY")
    
    # Test 2: DEBUG
    print_header("2. Verificación de DEBUG")
    total_tests += 1
    if test_result(
        settings.DEBUG == False,
        "DEBUG está en False",
        False,
        settings.DEBUG
    ):
        passed_tests += 1
    else:
        failed_tests.append("DEBUG")
    
    # Test 3: ALLOWED_HOSTS
    print_header("3. Verificación de ALLOWED_HOSTS")
    total_tests += 1
    expected_hosts = ['localhost', '127.0.0.1', 'testserver']
    if test_result(
        settings.ALLOWED_HOSTS == expected_hosts,
        "ALLOWED_HOSTS configurado correctamente",
        expected_hosts,
        settings.ALLOWED_HOSTS
    ):
        passed_tests += 1
    else:
        failed_tests.append("ALLOWED_HOSTS")
    
    # Test 4: CORS
    print_header("4. Verificación de CORS")
    total_tests += 1
    if test_result(
        settings.CORS_ALLOW_ALL_ORIGINS == False,
        "CORS_ALLOW_ALL_ORIGINS está en False",
        False,
        settings.CORS_ALLOW_ALL_ORIGINS
    ):
        passed_tests += 1
    else:
        failed_tests.append("CORS_ALLOW_ALL_ORIGINS")
    
    total_tests += 1
    expected_origins = ['http://localhost:3000', 'http://localhost:5173']
    if test_result(
        settings.CORS_ALLOWED_ORIGINS == expected_origins,
        "CORS_ALLOWED_ORIGINS configurado correctamente",
        expected_origins,
        settings.CORS_ALLOWED_ORIGINS
    ):
        passed_tests += 1
    else:
        failed_tests.append("CORS_ALLOWED_ORIGINS")
    
    # Test 5: REST Framework Permissions
    print_header("5. Verificación de Permisos REST Framework")
    total_tests += 1
    expected_permission = 'rest_framework.permissions.IsAuthenticated'
    actual_permission = settings.REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'][0]
    if test_result(
        actual_permission == expected_permission,
        "Permisos por defecto son IsAuthenticated",
        expected_permission,
        actual_permission
    ):
        passed_tests += 1
    else:
        failed_tests.append("REST_FRAMEWORK_PERMISSIONS")
    
    # Test 6: Rate Limiting
    print_header("6. Verificación de Rate Limiting")
    total_tests += 1
    expected_anon_rate = '100/hour'
    actual_anon_rate = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon']
    if test_result(
        actual_anon_rate == expected_anon_rate,
        "Rate limit para anónimos configurado",
        expected_anon_rate,
        actual_anon_rate
    ):
        passed_tests += 1
    else:
        failed_tests.append("RATE_LIMIT_ANON")
    
    total_tests += 1
    expected_user_rate = '1000/hour'
    actual_user_rate = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user']
    if test_result(
        actual_user_rate == expected_user_rate,
        "Rate limit para usuarios configurado",
        expected_user_rate,
        actual_user_rate
    ):
        passed_tests += 1
    else:
        failed_tests.append("RATE_LIMIT_USER")
    
    # Test 7: HTTPS Configuration (solo si DEBUG=False)
    print_header("7. Verificación de Configuración HTTPS")
    if not settings.DEBUG:
        total_tests += 1
        if test_result(
            hasattr(settings, 'SECURE_SSL_REDIRECT'),
            "SECURE_SSL_REDIRECT configurado",
            "Existe",
            "Existe" if hasattr(settings, 'SECURE_SSL_REDIRECT') else "No existe"
        ):
            passed_tests += 1
        else:
            failed_tests.append("SECURE_SSL_REDIRECT")
        
        total_tests += 1
        if test_result(
            hasattr(settings, 'SESSION_COOKIE_SECURE'),
            "SESSION_COOKIE_SECURE configurado",
            "Existe",
            "Existe" if hasattr(settings, 'SESSION_COOKIE_SECURE') else "No existe"
        ):
            passed_tests += 1
        else:
            failed_tests.append("SESSION_COOKIE_SECURE")
        
        total_tests += 1
        if test_result(
            hasattr(settings, 'CSRF_COOKIE_SECURE'),
            "CSRF_COOKIE_SECURE configurado",
            "Existe",
            "Existe" if hasattr(settings, 'CSRF_COOKIE_SECURE') else "No existe"
        ):
            passed_tests += 1
        else:
            failed_tests.append("CSRF_COOKIE_SECURE")
    else:
        print("⏭️  Saltando pruebas HTTPS (DEBUG=True)")
    
    # Test 8: CSRF Trusted Origins
    print_header("8. Verificación de CSRF Trusted Origins")
    total_tests += 1
    if test_result(
        hasattr(settings, 'CSRF_TRUSTED_ORIGINS'),
        "CSRF_TRUSTED_ORIGINS configurado",
        "Existe",
        "Existe" if hasattr(settings, 'CSRF_TRUSTED_ORIGINS') else "No existe"
    ):
        passed_tests += 1
    else:
        failed_tests.append("CSRF_TRUSTED_ORIGINS")
    
    # Test 9: Database Configuration
    print_header("9. Verificación de Base de Datos")
    total_tests += 1
    db_engine = settings.DATABASES['default']['ENGINE']
    if test_result(
        'sqlite3' in db_engine or 'postgresql' in db_engine or 'mysql' in db_engine,
        "Motor de base de datos configurado",
        "sqlite3/postgresql/mysql",
        db_engine
    ):
        passed_tests += 1
    else:
        failed_tests.append("DATABASE_ENGINE")
    
    # Test 10: Installed Apps
    print_header("10. Verificación de Apps Instaladas")
    required_apps = [
        'rest_framework',
        'rest_framework.authtoken',
        'corsheaders',
        'django_filters',
        'cmms_api'
    ]
    
    for app in required_apps:
        total_tests += 1
        if test_result(
            app in settings.INSTALLED_APPS,
            f"App '{app}' instalada",
            "Instalada",
            "Instalada" if app in settings.INSTALLED_APPS else "No instalada"
        ):
            passed_tests += 1
        else:
            failed_tests.append(f"APP_{app}")
    
    # Resumen
    print_header("📊 RESUMEN DE PRUEBAS")
    print(f"\nTotal de pruebas: {total_tests}")
    print(f"✅ Pruebas exitosas: {passed_tests}")
    print(f"❌ Pruebas fallidas: {total_tests - passed_tests}")
    print(f"📈 Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print("\n❌ Pruebas fallidas:")
        for test in failed_tests:
            print(f"   - {test}")
        print("\n⚠️  Algunas configuraciones necesitan revisión")
        return 1
    else:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ La configuración de seguridad es correcta")
        return 0

if __name__ == '__main__':
    sys.exit(main())
