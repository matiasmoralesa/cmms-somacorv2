#!/usr/bin/env python
"""
Script completo para verificar el sistema de login
"""
import os
import django
import requests
import json
from bs4 import BeautifulSoup

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def test_users_exist():
    """Verificar que los usuarios existen"""
    print("=" * 60)
    print("   VERIFICANDO USUARIOS")
    print("=" * 60)
    
    users = User.objects.all()
    for user in users:
        print(f"✅ Usuario: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Superusuario: {user.is_superuser}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Activo: {user.is_active}")
        
        # Verificar token
        try:
            token = Token.objects.get(user=user)
            print(f"   Token: {token.key}")
        except Token.DoesNotExist:
            print(f"   Token: No existe")
        print()

def test_api_login():
    """Probar login via API"""
    print("=" * 60)
    print("   PROBANDO LOGIN VIA API")
    print("=" * 60)
    
    test_users = [
        {'username': 'admin', 'password': 'admin123'},
        {'username': 'somacor_admin', 'password': 'Somacor2024!'},
        {'username': 'admin_somacor', 'password': 'Admin123!'}
    ]
    
    for user_data in test_users:
        try:
            response = requests.post(
                'http://localhost:8000/api/login/',
                json=user_data,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {user_data['username']}: Login exitoso")
                print(f"   Token: {data.get('token', 'No token')}")
            else:
                print(f"❌ {user_data['username']}: Error {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ {user_data['username']}: Error de conexión - {e}")
        print()

def test_django_admin():
    """Probar acceso al admin de Django"""
    print("=" * 60)
    print("   PROBANDO ADMIN DE DJANGO")
    print("=" * 60)
    
    test_users = [
        {'username': 'admin', 'password': 'admin123'},
        {'username': 'somacor_admin', 'password': 'Somacor2024!'},
        {'username': 'admin_somacor', 'password': 'Admin123!'}
    ]
    
    for user_data in test_users:
        try:
            session = requests.Session()
            
            # Obtener página de login
            login_page = session.get('http://localhost:8000/admin/login/', timeout=5)
            
            if login_page.status_code != 200:
                print(f"❌ {user_data['username']}: No se puede acceder a la página de login")
                continue
            
            # Extraer CSRF token
            soup = BeautifulSoup(login_page.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            
            if not csrf_input:
                print(f"❌ {user_data['username']}: No se encontró CSRF token")
                continue
            
            csrf_token = csrf_input['value']
            
            # Intentar login
            login_data = {
                'username': user_data['username'],
                'password': user_data['password'],
                'csrfmiddlewaretoken': csrf_token,
                'next': '/admin/'
            }
            
            login_response = session.post(
                'http://localhost:8000/admin/login/',
                data=login_data,
                timeout=5
            )
            
            if '/admin/' in login_response.url and 'login' not in login_response.url:
                print(f"✅ {user_data['username']}: Login exitoso en Django Admin")
            else:
                print(f"❌ {user_data['username']}: Login fallido en Django Admin")
                print(f"   URL final: {login_response.url}")
                
        except Exception as e:
            print(f"❌ {user_data['username']}: Error de conexión - {e}")
        print()

def test_backend_status():
    """Verificar estado del backend"""
    print("=" * 60)
    print("   VERIFICANDO ESTADO DEL BACKEND")
    print("=" * 60)
    
    endpoints = [
        'http://localhost:8000/',
        'http://localhost:8000/admin/',
        'http://localhost:8000/api/',
        'http://localhost:8000/api/v2/'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"✅ {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
    print()

if __name__ == '__main__':
    print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA DE LOGIN")
    print()
    
    test_backend_status()
    test_users_exist()
    test_api_login()
    test_django_admin()
    
    print("=" * 60)
    print("   VERIFICACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("💡 Si todos los tests pasan, el sistema de login está funcionando correctamente.")
    print("💡 Si hay errores, revisa los logs del servidor Django.")