#!/usr/bin/env python
"""
Script simple para crear datos de prueba básicos
"""
import os
import django
import sys
from datetime import datetime, timedelta
from django.utils import timezone

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import *
from django.contrib.auth.models import User

def create_basic_data():
    print("🚀 Creando datos básicos...")
    
    # Crear roles básicos
    rol_admin, _ = Roles.objects.get_or_create(
        idrol=1, defaults={'nombrerol': 'Administrador'}
    )
    rol_tecnico, _ = Roles.objects.get_or_create(
        idrol=2, defaults={'nombrerol': 'Técnico'}
    )
    print("✅ Roles creados")
    
    # Crear faenas básicas
    faena1, _ = Faenas.objects.get_or_create(
        idfaena=1, defaults={'nombrefaena': 'Faena Norte', 'activa': True}
    )
    faena2, _ = Faenas.objects.get_or_create(
        idfaena=2, defaults={'nombrefaena': 'Faena Sur', 'activa': True}
    )
    print("✅ Faenas creadas")
    
    # Crear tipos de equipo
    tipo1, _ = TiposEquipo.objects.get_or_create(
        idtipoequipo=1, defaults={'nombretipo': 'Minicargador'}
    )
    tipo2, _ = TiposEquipo.objects.get_or_create(
        idtipoequipo=2, defaults={'nombretipo': 'Excavadora'}
    )
    print("✅ Tipos de equipo creados")
    
    # Crear estados de equipo
    estado1, _ = EstadosEquipo.objects.get_or_create(
        idestadoequipo=1, defaults={'nombreestado': 'Operativo'}
    )
    estado2, _ = EstadosEquipo.objects.get_or_create(
        idestadoequipo=2, defaults={'nombreestado': 'En Mantenimiento'}
    )
    print("✅ Estados de equipo creados")
    
    # Crear equipos básicos
    equipo1, _ = Equipos.objects.get_or_create(
        idequipo=1,
        defaults={
            'nombreequipo': 'Minicargador CAT-001',
            'codigointerno': 'CAT-001',
            'marca': 'Caterpillar',
            'modelo': '226D',
            'anio': 2020,
            'patente': 'HJKL12',
            'idtipoequipo': tipo1,
            'idestadoactual': estado1,
            'idfaenaactual': faena1,
            'activo': True
        }
    )
    
    equipo2, _ = Equipos.objects.get_or_create(
        idequipo=2,
        defaults={
            'nombreequipo': 'Excavadora KOM-002',
            'codigointerno': 'KOM-002',
            'marca': 'Komatsu',
            'modelo': 'PC200-8',
            'anio': 2019,
            'patente': 'MNOP34',
            'idtipoequipo': tipo2,
            'idestadoactual': estado2,
            'idfaenaactual': faena2,
            'activo': True
        }
    )
    
    equipo3, _ = Equipos.objects.get_or_create(
        idequipo=3,
        defaults={
            'nombreequipo': 'Minicargador BOB-003',
            'codigointerno': 'BOB-003',
            'marca': 'Bobcat',
            'modelo': 'S650',
            'anio': 2021,
            'patente': 'QRST56',
            'idtipoequipo': tipo1,
            'idestadoactual': estado1,
            'idfaenaactual': faena1,
            'activo': True
        }
    )
    print("✅ Equipos creados")
    
    print("\n🎉 Datos básicos creados exitosamente!")
    print(f"- Equipos: {Equipos.objects.count()}")
    print(f"- Faenas: {Faenas.objects.count()}")
    print(f"- Tipos de equipo: {TiposEquipo.objects.count()}")

if __name__ == '__main__':
    create_basic_data()