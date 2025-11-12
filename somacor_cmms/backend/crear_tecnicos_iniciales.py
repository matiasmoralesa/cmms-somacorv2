"""
Script para crear especialidades y técnicos iniciales
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from django.contrib.auth.models import User
from cmms_api.models import Especialidades, Tecnicos
from datetime import date

def crear_especialidades():
    """Crear especialidades técnicas"""
    especialidades_data = [
        {'nombre': 'Compresores', 'descripcion': 'Mantenimiento y reparación de compresores de aire'},
        {'nombre': 'Sistemas Neumáticos', 'descripcion': 'Sistemas de aire comprimido y neumática'},
        {'nombre': 'Bombas Centrífugas', 'descripcion': 'Mantenimiento de bombas centrífugas'},
        {'nombre': 'Sistemas Hidráulicos', 'descripcion': 'Sistemas hidráulicos y oleohidráulicos'},
        {'nombre': 'Motores Eléctricos', 'descripcion': 'Mantenimiento de motores eléctricos'},
        {'nombre': 'Sistemas Eléctricos', 'descripcion': 'Instalaciones y sistemas eléctricos'},
        {'nombre': 'Automatización', 'descripcion': 'Sistemas de control y automatización'},
        {'nombre': 'Mantenimiento Preventivo', 'descripcion': 'Mantenimiento preventivo general'},
        {'nombre': 'Soldadura', 'descripcion': 'Trabajos de soldadura y fabricación'},
        {'nombre': 'Mecánica General', 'descripcion': 'Mecánica general y ajustes'},
    ]
    
    especialidades_creadas = []
    for esp_data in especialidades_data:
        esp, created = Especialidades.objects.get_or_create(
            nombreespecialidad=esp_data['nombre'],
            defaults={'descripcion': esp_data['descripcion']}
        )
        if created:
            print(f"✅ Especialidad creada: {esp.nombreespecialidad}")
        else:
            print(f"ℹ️  Especialidad ya existe: {esp.nombreespecialidad}")
        especialidades_creadas.append(esp)
    
    return especialidades_creadas


def crear_tecnicos(especialidades):
    """Crear técnicos de ejemplo"""
    tecnicos_data = [
        {
            'username': 'juan.perez',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan.perez@somacor.com',
            'telefono': '+56 9 1234 5678',
            'cargo': 'Técnico Senior',
            'estado': 'ocupado',
            'especialidades': ['Compresores', 'Sistemas Neumáticos', 'Mantenimiento Preventivo']
        },
        {
            'username': 'maria.garcia',
            'first_name': 'María',
            'last_name': 'García',
            'email': 'maria.garcia@somacor.com',
            'telefono': '+56 9 2345 6789',
            'cargo': 'Técnico Especialista',
            'estado': 'ocupado',
            'especialidades': ['Bombas Centrífugas', 'Sistemas Hidráulicos']
        },
        {
            'username': 'carlos.lopez',
            'first_name': 'Carlos',
            'last_name': 'López',
            'email': 'carlos.lopez@somacor.com',
            'telefono': '+56 9 3456 7890',
            'cargo': 'Técnico Eléctrico',
            'estado': 'disponible',
            'especialidades': ['Motores Eléctricos', 'Sistemas Eléctricos', 'Automatización']
        },
        {
            'username': 'ana.martinez',
            'first_name': 'Ana',
            'last_name': 'Martínez',
            'email': 'ana.martinez@somacor.com',
            'telefono': '+56 9 4567 8901',
            'cargo': 'Técnico Mecánico',
            'estado': 'disponible',
            'especialidades': ['Mecánica General', 'Soldadura', 'Mantenimiento Preventivo']
        },
        {
            'username': 'pedro.sanchez',
            'first_name': 'Pedro',
            'last_name': 'Sánchez',
            'email': 'pedro.sanchez@somacor.com',
            'telefono': '+56 9 5678 9012',
            'cargo': 'Técnico Junior',
            'estado': 'disponible',
            'especialidades': ['Mantenimiento Preventivo', 'Mecánica General']
        }
    ]
    
    for tec_data in tecnicos_data:
        # Crear o obtener usuario
        user, user_created = User.objects.get_or_create(
            username=tec_data['username'],
            defaults={
                'first_name': tec_data['first_name'],
                'last_name': tec_data['last_name'],
                'email': tec_data['email']
            }
        )
        
        if user_created:
            user.set_password('password123')  # Contraseña temporal
            user.save()
            print(f"✅ Usuario creado: {user.username}")
        else:
            print(f"ℹ️  Usuario ya existe: {user.username}")
        
        # Crear o obtener técnico
        tecnico, tec_created = Tecnicos.objects.get_or_create(
            usuario=user,
            defaults={
                'telefono': tec_data['telefono'],
                'email': tec_data['email'],
                'cargo': tec_data['cargo'],
                'estado': tec_data['estado'],
                'fecha_ingreso': date.today()
            }
        )
        
        if tec_created:
            print(f"✅ Técnico creado: {tecnico.nombre_completo}")
            
            # Asignar especialidades
            for esp_nombre in tec_data['especialidades']:
                esp = next((e for e in especialidades if e.nombreespecialidad == esp_nombre), None)
                if esp:
                    tecnico.especialidades.add(esp)
            
            print(f"   Especialidades: {', '.join(tec_data['especialidades'])}")
        else:
            print(f"ℹ️  Técnico ya existe: {tecnico.nombre_completo}")


def main():
    print("=" * 60)
    print("CREANDO ESPECIALIDADES Y TÉCNICOS INICIALES")
    print("=" * 60)
    print()
    
    print("1. Creando especialidades...")
    print("-" * 60)
    especialidades = crear_especialidades()
    print()
    
    print("2. Creando técnicos...")
    print("-" * 60)
    crear_tecnicos(especialidades)
    print()
    
    print("=" * 60)
    print("✅ PROCESO COMPLETADO")
    print("=" * 60)
    print()
    print(f"Total especialidades: {Especialidades.objects.count()}")
    print(f"Total técnicos: {Tecnicos.objects.count()}")
    print()


if __name__ == '__main__':
    main()
