#!/usr/bin/env python3
"""
Script de verificación de configuración para producción
Verifica que todas las configuraciones críticas estén correctas
"""
import os
import sys

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def check_item(condition, message, critical=False):
    if condition:
        print(f"✅ {message}")
        return True
    else:
        symbol = "🔥" if critical else "⚠️"
        print(f"{symbol} {message}")
        return False

def main():
    print_header("🔍 VERIFICACIÓN DE CONFIGURACIÓN PARA PRODUCCIÓN")
    
    all_ok = True
    critical_errors = []
    warnings = []
    
    # Verificar archivo .env
    print_header("1. Verificación de Archivos de Configuración")
    
    env_exists = os.path.exists('somacor_cmms/backend/.env')
    if check_item(env_exists, "Archivo .env existe", critical=True):
        print("   📝 Recuerda configurar todas las variables en .env")
    else:
        critical_errors.append("Archivo .env no existe")
        print("   💡 Ejecuta: cp somacor_cmms/backend/.env.example somacor_cmms/backend/.env")
    
    env_example_exists = os.path.exists('somacor_cmms/backend/.env.example')
    check_item(env_example_exists, "Archivo .env.example existe")
    
    # Verificar archivos de código
    print_header("2. Verificación de Archivos de Código")
    
    settings_exists = os.path.exists('somacor_cmms/backend/cmms_project/settings.py')
    check_item(settings_exists, "settings.py existe", critical=True)
    
    health_exists = os.path.exists('somacor_cmms/backend/cmms_api/views_health.py')
    check_item(health_exists, "views_health.py existe (Health checks)")
    
    urls_exists = os.path.exists('somacor_cmms/backend/cmms_project/urls.py')
    check_item(urls_exists, "urls.py existe", critical=True)
    
    # Verificar configuraciones en settings.py
    print_header("3. Verificación de Configuraciones de Seguridad")
    
    if settings_exists:
        with open('somacor_cmms/backend/cmms_project/settings.py', 'r', encoding='utf-8') as f:
            settings_content = f.read()
        
        # Verificar SECRET_KEY
        has_secret_key_check = "if not SECRET_KEY:" in settings_content
        if check_item(has_secret_key_check, "SECRET_KEY tiene validación", critical=True):
            print("   ✅ SECRET_KEY forzada en producción")
        else:
            critical_errors.append("SECRET_KEY no tiene validación")
        
        # Verificar DEBUG
        debug_default_false = "os.environ.get('DJANGO_DEBUG', 'False')" in settings_content
        if check_item(debug_default_false, "DEBUG=False por defecto", critical=True):
            print("   ✅ DEBUG seguro por defecto")
        else:
            critical_errors.append("DEBUG no es False por defecto")
        
        # Verificar ALLOWED_HOSTS
        allowed_hosts_env = "os.environ.get('DJANGO_ALLOWED_HOSTS'" in settings_content
        if check_item(allowed_hosts_env, "ALLOWED_HOSTS desde variable de entorno", critical=True):
            print("   ✅ ALLOWED_HOSTS configurable")
        else:
            critical_errors.append("ALLOWED_HOSTS no configurable")
        
        # Verificar CORS
        cors_configurable = "os.environ.get('CORS_ALLOW_ALL_ORIGINS'" in settings_content
        if check_item(cors_configurable, "CORS configurable desde .env", critical=True):
            print("   ✅ CORS restringible")
        else:
            critical_errors.append("CORS no configurable")
        
        # Verificar permisos
        is_authenticated = "'rest_framework.permissions.IsAuthenticated'" in settings_content
        if check_item(is_authenticated, "Permisos IsAuthenticated por defecto", critical=True):
            print("   ✅ API segura por defecto")
        else:
            critical_errors.append("Permisos no son IsAuthenticated")
        
        # Verificar HTTPS config
        has_https_config = "SECURE_SSL_REDIRECT" in settings_content
        if check_item(has_https_config, "Configuración HTTPS presente"):
            print("   ✅ Configuración HTTPS implementada")
        else:
            warnings.append("Falta configuración HTTPS")
        
        # Verificar CSRF
        has_csrf_config = "CSRF_TRUSTED_ORIGINS" in settings_content
        if check_item(has_csrf_config, "Configuración CSRF presente"):
            print("   ✅ CSRF configurado")
        else:
            warnings.append("Falta configuración CSRF")
    
    # Verificar documentación
    print_header("4. Verificación de Documentación")
    
    analisis_exists = os.path.exists('ANALISIS_PRODUCCION_COMPLETO.md')
    check_item(analisis_exists, "Análisis de producción existe")
    
    guia_exists = os.path.exists('GUIA_DESPLIEGUE_SEGURO.md')
    check_item(guia_exists, "Guía de despliegue existe")
    
    correcciones_exists = os.path.exists('CORRECCIONES_APLICADAS.md')
    check_item(correcciones_exists, "Documento de correcciones existe")
    
    # Verificar requirements.txt
    print_header("5. Verificación de Dependencias")
    
    requirements_exists = os.path.exists('somacor_cmms/backend/requirements.txt')
    if check_item(requirements_exists, "requirements.txt existe"):
        with open('somacor_cmms/backend/requirements.txt', 'r', encoding='utf-8') as f:
            requirements_content = f.read()
        
        has_psycopg2 = 'psycopg2-binary' in requirements_content
        check_item(has_psycopg2, "PostgreSQL driver incluido")
        
        has_gunicorn = 'gunicorn' in requirements_content
        check_item(has_gunicorn, "Gunicorn incluido")
        
        has_whitenoise = 'whitenoise' in requirements_content
        check_item(has_whitenoise, "WhiteNoise incluido")
        
        has_redis = 'redis' in requirements_content
        check_item(has_redis, "Redis incluido")
        
        has_psutil = 'psutil' in requirements_content
        check_item(has_psutil, "psutil incluido (para health checks)")
    
    # Resumen final
    print_header("📊 RESUMEN DE VERIFICACIÓN")
    
    if critical_errors:
        print("\n🔥 ERRORES CRÍTICOS ENCONTRADOS:")
        for error in critical_errors:
            print(f"   - {error}")
        print("\n❌ EL SISTEMA NO ESTÁ LISTO PARA PRODUCCIÓN")
        print("   Corrige los errores críticos antes de desplegar")
    elif warnings:
        print("\n⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"   - {warning}")
        print("\n⚠️  EL SISTEMA ESTÁ CASI LISTO")
        print("   Revisa las advertencias antes de desplegar")
    else:
        print("\n✅ TODAS LAS VERIFICACIONES PASARON")
        print("\n🎉 EL SISTEMA ESTÁ LISTO PARA PRODUCCIÓN")
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Configurar archivo .env con valores reales")
        print("   2. Generar SECRET_KEY única")
        print("   3. Configurar PostgreSQL")
        print("   4. Seguir GUIA_DESPLIEGUE_SEGURO.md")
    
    print("\n" + "=" * 80)
    print("Para más información, consulta:")
    print("  - ANALISIS_PRODUCCION_COMPLETO.md")
    print("  - GUIA_DESPLIEGUE_SEGURO.md")
    print("  - CORRECCIONES_APLICADAS.md")
    print("=" * 80 + "\n")
    
    return 0 if not critical_errors else 1

if __name__ == '__main__':
    sys.exit(main())
