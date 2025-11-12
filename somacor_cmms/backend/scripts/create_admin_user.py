#!/usr/bin/env python
"""
Script para crear el usuario admin con rol asignado
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from django.contrib.auth.models import User
from cmms_api.models import Roles, Usuarios

def create_admin_with_role():
    print("🚀 Creando usuario admin con rol...")
    
    # Crear o obtener el rol de Administrador
    rol_admin, created = Roles.objects.get_or_create(
        idrol=1,
        defaults={'nombrerol': 'Administrador', 'departamento': 'TI'}
    )
    if created:
        print("✅ Rol Administrador creado")
    else:
        print("✅ Rol Administrador ya existe")
    
    # Crear o actualizar el usuario Django admin
    django_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'email': 'admin@somacor.com',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    
    if created:
        django_user.set_password('admin123')
        django_user.save()
        print("✅ Usuario Django admin creado")
    else:
        # Asegurar que tenga la contraseña correcta
        django_user.set_password('admin123')
        django_user.is_staff = True
        django_user.is_superuser = True
        django_user.is_active = True
        django_user.save()
        print("✅ Usuario Django admin actualizado")
    
    # Crear o actualizar el perfil de usuario en el sistema CMMS
    usuario_cmms, created = Usuarios.objects.get_or_create(
        user=django_user,
        defaults={
            'idrol': rol_admin,
            'departamento': 'Administración'
        }
    )
    
    if created:
        print("✅ Perfil CMMS para admin creado")
    else:
        # Asegurar que tenga el rol correcto
        usuario_cmms.idrol = rol_admin
        usuario_cmms.departamento = 'Administración'
        usuario_cmms.save()
        print("✅ Perfil CMMS para admin actualizado")
    
    # Crear token de autenticación
    from rest_framework.authtoken.models import Token
    token, created = Token.objects.get_or_create(user=django_user)
    if created:
        print("✅ Token de autenticación creado")
    else:
        print("✅ Token de autenticación ya existe")
    
    print(f"\n🎉 Usuario admin configurado correctamente!")
    print(f"📋 Detalles:")
    print(f"   - Usuario: admin")
    print(f"   - Contraseña: admin123")
    print(f"   - Rol: {rol_admin.nombrerol}")
    print(f"   - Departamento: {usuario_cmms.departamento}")
    print(f"   - Token: {token.key}")
    print(f"   - Es staff: {django_user.is_staff}")
    print(f"   - Es superuser: {django_user.is_superuser}")

if __name__ == '__main__':
    create_admin_with_role()