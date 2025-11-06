#!/usr/bin/env python
"""
Script simple para crear órdenes de trabajo de prueba
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

def create_simple_orders():
    print("🚀 Creando órdenes de trabajo simples...")
    
    # Obtener datos necesarios
    admin_user = User.objects.get(username='admin')
    equipos = list(Equipos.objects.all()[:3])
    
    if not equipos:
        print("❌ No hay equipos")
        return
    
    # Crear tipos de mantenimiento
    tipo_preventivo, _ = TiposMantenimientoOT.objects.get_or_create(
        idtipomantenimientoot=1,
        defaults={'nombretipomantenimientoot': 'Preventivo'}
    )
    
    tipo_correctivo, _ = TiposMantenimientoOT.objects.get_or_create(
        idtipomantenimientoot=2,
        defaults={'nombretipomantenimientoot': 'Correctivo'}
    )
    
    # Crear estados
    estado_pendiente, _ = EstadosOrdenTrabajo.objects.get_or_create(
        idestadoot=1,
        defaults={'nombreestadoot': 'Pendiente'}
    )
    
    estado_completada, _ = EstadosOrdenTrabajo.objects.get_or_create(
        idestadoot=2,
        defaults={'nombreestadoot': 'Completada'}
    )
    
    estado_en_proceso, _ = EstadosOrdenTrabajo.objects.get_or_create(
        idestadoot=3,
        defaults={'nombreestadoot': 'En Proceso'}
    )
    
    # Crear órdenes simples
    ordenes = [
        {
            'numeroot': 'OT-001',
            'idequipo': equipos[0],
            'idsolicitante': admin_user,
            'idtecnicoasignado': admin_user,
            'idtipomantenimientoot': tipo_preventivo,
            'idestadoot': estado_completada,
            'descripcionproblemareportado': 'Mantenimiento preventivo - Cambio de aceite',
            'prioridad': 'Media',
            'fechacompletado': timezone.now() - timedelta(days=2),
            'tiempototalminutos': 120
        },
        {
            'numeroot': 'OT-002',
            'idequipo': equipos[1] if len(equipos) > 1 else equipos[0],
            'idsolicitante': admin_user,
            'idtecnicoasignado': admin_user,
            'idtipomantenimientoot': tipo_correctivo,
            'idestadoot': estado_en_proceso,
            'descripcionproblemareportado': 'Falla en sistema hidráulico',
            'prioridad': 'Alta',
            'tiempototalminutos': 180
        },
        {
            'numeroot': 'OT-003',
            'idequipo': equipos[2] if len(equipos) > 2 else equipos[0],
            'idsolicitante': admin_user,
            'idtecnicoasignado': admin_user,
            'idtipomantenimientoot': tipo_preventivo,
            'idestadoot': estado_pendiente,
            'descripcionproblemareportado': 'Revisión de frenos',
            'prioridad': 'Media',
            'tiempototalminutos': 90
        },
        {
            'numeroot': 'OT-004',
            'idequipo': equipos[0],
            'idsolicitante': admin_user,
            'idtecnicoasignado': admin_user,
            'idtipomantenimientoot': tipo_correctivo,
            'idestadoot': estado_pendiente,
            'descripcionproblemareportado': 'Motor sobrecalentado - URGENTE',
            'prioridad': 'Crítica',
            'tiempototalminutos': 240
        }
    ]
    
    for i, orden_data in enumerate(ordenes, 1):
        # Ajustar fechas
        orden_data['fechacreacionot'] = timezone.now() - timedelta(days=i)
        if orden_data['idestadoot'] == estado_pendiente and i == 4:
            # Hacer que la orden 4 sea vencida (más de 7 días)
            orden_data['fechacreacionot'] = timezone.now() - timedelta(days=10)
        
        orden, created = OrdenesTrabajo.objects.get_or_create(
            numeroot=orden_data['numeroot'],
            defaults=orden_data
        )
        
        if created:
            print(f"✅ Orden {orden_data['numeroot']} creada")
        else:
            print(f"ℹ️ Orden {orden_data['numeroot']} ya existe")
    
    print(f"\n🎉 Órdenes creadas!")
    print(f"📊 Total: {OrdenesTrabajo.objects.count()}")
    print(f"📊 Pendientes: {OrdenesTrabajo.objects.filter(idestadoot__nombreestadoot='Pendiente').count()}")
    print(f"📊 Completadas: {OrdenesTrabajo.objects.filter(idestadoot__nombreestadoot='Completada').count()}")

if __name__ == '__main__':
    create_simple_orders()