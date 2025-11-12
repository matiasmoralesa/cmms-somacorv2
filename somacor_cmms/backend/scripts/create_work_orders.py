#!/usr/bin/env python
"""
Script para crear órdenes de trabajo de prueba
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

def create_work_orders():
    print("🚀 Creando órdenes de trabajo de prueba...")
    
    # Verificar que existan los modelos necesarios
    try:
        # Obtener equipos existentes
        equipos = list(Equipos.objects.all()[:3])
        if not equipos:
            print("❌ No hay equipos en la base de datos")
            return
        
        # Obtener usuarios Django existentes
        usuarios_django = list(User.objects.all()[:2])
        if not usuarios_django:
            print("❌ No hay usuarios Django en la base de datos")
            return
        
        # Crear tipos de mantenimiento OT si no existen
        tipo_preventivo, _ = TiposMantenimientoOT.objects.get_or_create(
            idtipomantenimientoot=1,
            defaults={'nombretipomantenimientoot': 'Preventivo'}
        )
        
        tipo_correctivo, _ = TiposMantenimientoOT.objects.get_or_create(
            idtipomantenimientoot=2,
            defaults={'nombretipomantenimientoot': 'Correctivo'}
        )
        
        tipo_emergencia, _ = TiposMantenimientoOT.objects.get_or_create(
            idtipomantenimientoot=3,
            defaults={'nombretipomantenimientoot': 'Emergencia'}
        )
        
        print("✅ Tipos de mantenimiento creados")
        
        # Crear estados de orden de trabajo si no existen
        estado_pendiente, _ = EstadosOrdenTrabajo.objects.get_or_create(
            idestadoot=1,
            defaults={'nombreestadoot': 'Pendiente'}
        )
        
        estado_en_proceso, _ = EstadosOrdenTrabajo.objects.get_or_create(
            idestadoot=2,
            defaults={'nombreestadoot': 'En Proceso'}
        )
        
        estado_completada, _ = EstadosOrdenTrabajo.objects.get_or_create(
            idestadoot=3,
            defaults={'nombreestadoot': 'Completada'}
        )
        
        print("✅ Estados de OT creados")
        
        # Crear órdenes de trabajo de ejemplo
        ordenes_data = [
            {
                'numeroot': 'OT-2024-001',
                'descripcionproblemareportado': 'Mantenimiento preventivo - Cambio de aceite y filtros',
                'prioridad': 'Media',
                'idequipo': equipos[0],
                'idsolicitante': usuarios_django[0],
                'idtecnicoasignado': usuarios_django[0],
                'idestadoot': estado_completada,
                'idtipomantenimientoot': tipo_preventivo,
                'fechacreacionot': timezone.now() - timedelta(days=5),
                'fechacompletado': timezone.now() - timedelta(days=2),
                'tiempototalminutos': 120
            },
            {
                'numeroot': 'OT-2024-002',
                'descripcionproblemareportado': 'Falla en sistema hidráulico - Pérdida de presión',
                'prioridad': 'Alta',
                'idequipo': equipos[1] if len(equipos) > 1 else equipos[0],
                'idsolicitante': usuarios[0],
                'idtecnicoasignado': usuarios[0],
                'idestadoot': estado_en_proceso,
                'idtipomantenimientoot': tipo_correctivo,
                'fechacreacionot': timezone.now() - timedelta(days=3),
                'tiempototalminutos': 180
            },
            {
                'numeroot': 'OT-2024-003',
                'descripcionproblemareportado': 'Revisión de frenos y sistema de dirección',
                'prioridad': 'Media',
                'idequipo': equipos[2] if len(equipos) > 2 else equipos[0],
                'idsolicitante': usuarios[0],
                'idtecnicoasignado': usuarios[0],
                'idestadoot': estado_pendiente,
                'idtipomantenimientoot': tipo_preventivo,
                'fechacreacionot': timezone.now() - timedelta(days=1),
                'tiempototalminutos': 90
            },
            {
                'numeroot': 'OT-2024-004',
                'descripcionproblemareportado': 'Motor sobrecalentado - Requiere atención inmediata',
                'prioridad': 'Crítica',
                'idequipo': equipos[0],
                'idsolicitante': usuarios[0],
                'idtecnicoasignado': usuarios[0],
                'idestadoot': estado_pendiente,
                'idtipomantenimientoot': tipo_emergencia,
                'fechacreacionot': timezone.now() - timedelta(days=8),  # Orden vencida
                'tiempototalminutos': 240
            },
            {
                'numeroot': 'OT-2024-005',
                'descripcionproblemareportado': 'Mantenimiento 1000 horas - Revisión general',
                'prioridad': 'Media',
                'idequipo': equipos[1] if len(equipos) > 1 else equipos[0],
                'idsolicitante': usuarios[0],
                'idtecnicoasignado': usuarios[0],
                'idestadoot': estado_completada,
                'idtipomantenimientoot': tipo_preventivo,
                'fechacreacionot': timezone.now() - timedelta(days=15),
                'fechacompletado': timezone.now() - timedelta(days=10),
                'tiempototalminutos': 300
            }
        ]
        
        # Crear las órdenes
        for i, orden_data in enumerate(ordenes_data, 1):
            orden, created = OrdenesTrabajo.objects.get_or_create(
                idordentrabajo=i,
                defaults=orden_data
            )
            if created:
                print(f"✅ Orden {orden_data['numeroot']} creada")
            else:
                print(f"ℹ️ Orden {orden_data['numeroot']} ya existe")
        
        print(f"\n🎉 Órdenes de trabajo creadas exitosamente!")
        print(f"📊 Resumen:")
        print(f"   - Total órdenes: {OrdenesTrabajo.objects.count()}")
        print(f"   - Pendientes: {OrdenesTrabajo.objects.filter(idestadoot__nombreestadoot='Pendiente').count()}")
        print(f"   - En proceso: {OrdenesTrabajo.objects.filter(idestadoot__nombreestadoot='En Proceso').count()}")
        print(f"   - Completadas: {OrdenesTrabajo.objects.filter(idestadoot__nombreestadoot='Completada').count()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_work_orders()