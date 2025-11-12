#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de prueba
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

def create_test_data():
    print("🚀 Creando datos de prueba...")
    
    # Crear roles si no existen
    rol_admin, created = Roles.objects.get_or_create(
        idrol=1,
        defaults={'nombrerol': 'Administrador', 'departamento': 'TI'}
    )
    if created:
        print("✅ Rol Administrador creado")
    
    rol_tecnico, created = Roles.objects.get_or_create(
        idrol=2,
        defaults={'nombrerol': 'Técnico', 'departamento': 'Mantenimiento'}
    )
    if created:
        print("✅ Rol Técnico creado")
    
    # Crear faenas si no existen
    faena1, created = Faenas.objects.get_or_create(
        idfaena=1,
        defaults={'nombrefaena': 'Faena Norte', 'ubicacion': 'Región Norte', 'activa': True}
    )
    if created:
        print("✅ Faena Norte creada")
    
    faena2, created = Faenas.objects.get_or_create(
        idfaena=2,
        defaults={'nombrefaena': 'Faena Sur', 'ubicacion': 'Región Sur', 'activa': True}
    )
    if created:
        print("✅ Faena Sur creada")
    
    # Crear tipos de equipo si no existen
    tipo_equipo1, created = TiposEquipo.objects.get_or_create(
        idtipoequipo=1,
        defaults={'nombretipo': 'Minicargador'}
    )
    if created:
        print("✅ Tipo Minicargador creado")
    
    tipo_equipo2, created = TiposEquipo.objects.get_or_create(
        idtipoequipo=2,
        defaults={'nombretipo': 'Excavadora'}
    )
    if created:
        print("✅ Tipo Excavadora creado")
    
    # Crear estados de equipo si no existen
    estado_operativo, created = EstadosEquipo.objects.get_or_create(
        idestadoequipo=1,
        defaults={'nombreestado': 'Operativo'}
    )
    if created:
        print("✅ Estado Operativo creado")
    
    estado_mantenimiento, created = EstadosEquipo.objects.get_or_create(
        idestadoequipo=2,
        defaults={'nombreestado': 'En Mantenimiento'}
    )
    if created:
        print("✅ Estado En Mantenimiento creado")
    
    # Crear usuarios Django primero
    from django.contrib.auth.models import User
    
    django_user1, created = User.objects.get_or_create(
        username='juan.perez',
        defaults={
            'first_name': 'Juan Carlos',
            'last_name': 'Pérez González',
            'email': 'juan.perez@somacor.com',
            'is_active': True
        }
    )
    if created:
        print("✅ Usuario Django juan.perez creado")
    
    django_user2, created = User.objects.get_or_create(
        username='maria.rodriguez',
        defaults={
            'first_name': 'María Elena',
            'last_name': 'Rodríguez Silva',
            'email': 'maria.rodriguez@somacor.com',
            'is_active': True
        }
    )
    if created:
        print("✅ Usuario Django maria.rodriguez creado")
    
    # Crear usuarios/técnicos si no existen
    usuario1, created = Usuarios.objects.get_or_create(
        user=django_user1,
        defaults={
            'idrol': rol_tecnico,
            'departamento': 'Mantenimiento'
        }
    )
    if created:
        print("✅ Usuario Juan Carlos creado")
    
    usuario2, created = Usuarios.objects.get_or_create(
        user=django_user2,
        defaults={
            'idrol': rol_tecnico,
            'departamento': 'Mantenimiento'
        }
    )
    if created:
        print("✅ Usuario María Elena creado")
    
    # Crear equipos si no existen
    equipo1, created = Equipos.objects.get_or_create(
        idequipo=1,
        defaults={
            'nombreequipo': 'Minicargador CAT-001',
            'codigointerno': 'CAT-001',
            'marca': 'Caterpillar',
            'modelo': '226D',
            'anio': 2020,
            'patente': 'HJKL12',
            'idtipoequipo': tipo_equipo1,
            'idestadoactual': estado_operativo,
            'idfaenaactual': faena1,
            'activo': True,
            'fechacreacion': timezone.now()
        }
    )
    if created:
        print("✅ Equipo Minicargador CAT-001 creado")
    
    equipo2, created = Equipos.objects.get_or_create(
        idequipo=2,
        defaults={
            'nombreequipo': 'Excavadora KOM-002',
            'codigointerno': 'KOM-002',
            'marca': 'Komatsu',
            'modelo': 'PC200-8',
            'anio': 2019,
            'patente': 'MNOP34',
            'idtipoequipo': tipo_equipo2,
            'idestadoactual': estado_mantenimiento,
            'idfaenaactual': faena2,
            'activo': True,
            'fechacreacion': timezone.now()
        }
    )
    if created:
        print("✅ Equipo Excavadora KOM-002 creado")
    
    equipo3, created = Equipos.objects.get_or_create(
        idequipo=3,
        defaults={
            'nombreequipo': 'Minicargador BOB-003',
            'codigointerno': 'BOB-003',
            'marca': 'Bobcat',
            'modelo': 'S650',
            'anio': 2021,
            'patente': 'QRST56',
            'idtipoequipo': tipo_equipo1,
            'idestadoactual': estado_operativo,
            'idfaenaactual': faena1,
            'activo': True,
            'fechacreacion': timezone.now()
        }
    )
    if created:
        print("✅ Equipo Minicargador BOB-003 creado")
    
    # Crear tipos de mantenimiento OT si no existen
    tipo_preventivo, created = TiposMantenimientoOT.objects.get_or_create(
        idtipomantenimientoot=1,
        defaults={'nombretipomantenimientoot': 'Preventivo', 'activo': True}
    )
    if created:
        print("✅ Tipo Mantenimiento Preventivo creado")
    
    tipo_correctivo, created = TiposMantenimientoOT.objects.get_or_create(
        idtipomantenimientoot=2,
        defaults={'nombretipomantenimientoot': 'Correctivo', 'activo': True}
    )
    if created:
        print("✅ Tipo Mantenimiento Correctivo creado")
    
    # Crear estados de orden de trabajo si no existen
    estado_pendiente, created = EstadosOrdenTrabajo.objects.get_or_create(
        idestadoot=1,
        defaults={'nombreestadoot': 'Pendiente', 'activo': True}
    )
    if created:
        print("✅ Estado OT Pendiente creado")
    
    estado_completada, created = EstadosOrdenTrabajo.objects.get_or_create(
        idestadoot=2,
        defaults={'nombreestadoot': 'Completada', 'activo': True}
    )
    if created:
        print("✅ Estado OT Completada creado")
    
    estado_en_proceso, created = EstadosOrdenTrabajo.objects.get_or_create(
        idestadoot=3,
        defaults={'nombreestadoot': 'En Proceso', 'activo': True}
    )
    if created:
        print("✅ Estado OT En Proceso creado")
    
    # Crear órdenes de trabajo de ejemplo
    ordenes_data = [
        {
            'numeroot': 'OT-2024-001',
            'descripcionproblemareportado': 'Revisión preventiva de motor y sistemas hidráulicos',
            'prioridad': 'Media',
            'idequipo': equipo1,
            'idsolicitante': usuario1,
            'idtecnicoasignado': usuario2,
            'idestadoot': estado_completada,
            'idtipomantenimientoot': tipo_preventivo,
            'fechacreacion': timezone.now() - timedelta(days=5),
            'fechacompletado': timezone.now() - timedelta(days=2)
        },
        {
            'numeroot': 'OT-2024-002',
            'descripcionproblemareportado': 'Falla en sistema hidráulico - pérdida de presión',
            'prioridad': 'Alta',
            'idequipo': equipo2,
            'idsolicitante': usuario2,
            'idtecnicoasignado': usuario1,
            'idestadoot': estado_en_proceso,
            'idtipomantenimientoot': tipo_correctivo,
            'fechacreacion': timezone.now() - timedelta(days=3)
        },
        {
            'numeroot': 'OT-2024-003',
            'descripcionproblemareportado': 'Cambio de aceite y filtros programado',
            'prioridad': 'Baja',
            'idequipo': equipo3,
            'idsolicitante': usuario1,
            'idtecnicoasignado': usuario2,
            'idestadoot': estado_pendiente,
            'idtipomantenimientoot': tipo_preventivo,
            'fechacreacion': timezone.now() - timedelta(days=1)
        },
        {
            'numeroot': 'OT-2024-004',
            'descripcionproblemareportado': 'Ruido extraño en motor - requiere diagnóstico',
            'prioridad': 'Crítica',
            'idequipo': equipo1,
            'idsolicitante': usuario2,
            'idtecnicoasignado': usuario1,
            'idestadoot': estado_pendiente,
            'idtipomantenimientoot': tipo_correctivo,
            'fechacreacion': timezone.now() - timedelta(days=8)  # Orden vencida
        },
        {
            'numeroot': 'OT-2024-005',
            'descripcionproblemareportado': 'Mantenimiento preventivo 500 horas',
            'prioridad': 'Media',
            'idequipo': equipo2,
            'idsolicitante': usuario1,
            'idtecnicoasignado': usuario2,
            'idestadoot': estado_completada,
            'idtipomantenimientoot': tipo_preventivo,
            'fechacreacion': timezone.now() - timedelta(days=15),
            'fechacompletado': timezone.now() - timedelta(days=10)
        }
    ]
    
    for i, orden_data in enumerate(ordenes_data, 1):
        orden, created = OrdenesTrabajo.objects.get_or_create(
            idordentrabajo=i,
            defaults=orden_data
        )
        if created:
            print(f"✅ Orden de Trabajo {orden_data['numeroot']} creada")
    
    print("\n🎉 Datos de prueba creados exitosamente!")
    print("\n📊 Resumen:")
    print(f"- Equipos: {Equipos.objects.count()}")
    print(f"- Órdenes de Trabajo: {OrdenesTrabajo.objects.count()}")
    print(f"- Usuarios: {Usuarios.objects.count()}")
    print(f"- Faenas: {Faenas.objects.count()}")

if __name__ == '__main__':
    create_test_data()