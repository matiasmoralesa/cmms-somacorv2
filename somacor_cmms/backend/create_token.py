"""
Script para crear un token de autenticación para el usuario admin
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def create_or_get_token(username='admin'):
    """Crea o obtiene el token para un usuario"""
    try:
        user = User.objects.get(username=username)
        token, created = Token.objects.get_or_create(user=user)
        
        if created:
            print(f"✅ Token creado para usuario '{username}':")
        else:
            print(f"✅ Token existente para usuario '{username}':")
        
        print(f"\n🔑 Token: {token.key}")
        print(f"\n📋 Copia este token y pégalo en la consola del navegador:")
        print(f"   localStorage.setItem('authToken', '{token.key}');")
        print(f"\n💡 O recarga la página después de ejecutar el script de autenticación.")
        
        return token.key
    except User.DoesNotExist:
        print(f"❌ Error: El usuario '{username}' no existe.")
        print(f"\n💡 Ejecuta primero el script de creación de superusuario:")
        print(f"   python manage.py createsuperuser")
        return None

if __name__ == '__main__':
    print("=" * 60)
    print("   GENERADOR DE TOKEN DE AUTENTICACIÓN")
    print("=" * 60)
    print()
    
    # Crear token para admin
    create_or_get_token('admin')
    
    print()
    print("=" * 60)
    print("   SCRIPT COMPLETADO")
    print("=" * 60)
