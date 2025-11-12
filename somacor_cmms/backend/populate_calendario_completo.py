"""
Script para poblar datos completos para el calendario
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import (
    Equipos, TiposEquipo, EstadosEquipo, Faenas,
    OrdenesTrabajo, EstadosOrdenTrabajo, TiposMantenimientoOT
)
from django.contrib.auth.models import User

def populate_all():
    print("🔧 Poblando datos para el calendario...")
    
    # Obtener usuario
    usuario = User.objects.first()
    if not usuario:
        print("❌ No hay usuarios. Crea un usuario primero.")
        return
    
    # Crear tipos de equipo si no existen
    tipo_equipo, _ = TiposEquipo.objects.get_or_create(
        nombretipo='Camión Minero',
        defaults={}
    )
    
    # Crear estados de equipo si no existen
    estado_operativo, _ = EstadosEquipo.objects.get_or_create(
        nombreestado='Operativo',
        defaults={}
    )
    
    # Crear faena si no existe
    faena, _ = Faenas.objects.get_or_create(
        nombrefaena='Mina Principal',
        defaults={
            'ubicacion': 'Región de Antofagasta',
            'descripcion': 'Faena principal de operaciones'
        }
    )
    
    # Crear equipos si no existen
    equipos_data = [
        {'nombre': 'CAT-797F-001', 'marca': 'Caterpillar', 'modelo': '797F'},
        {'nombre': 'KOM-930E-002', 'marca': 'Komatsu', 'modelo': '930E'},
        {'nombre': 'CAT-797F-003', 'marca': 'Caterpillar', 'modelo': '797F'},
        {'nombre': 'KOM-930E-004', 'marca': 'Komatsu', 'modelo': '930E'},
        {'nombre': 'CAT-797F-005', 'marca': 'Caterpillar', 'modelo': '797F'},
    ]
    
    equipos = []
    for eq_data in equipos_data:
        equipo, created = Equipos.objects.get_or_create(
            nombreequipo=eq_data['nombre'],
            defaults={
                'idtipoequipo': tipo_equipo,
                'idestadoactual': estado_operativo,
                'idfaenaactual': faena,
                'marca': eq_data['marca'],
                'modelo': eq_data['modelo'],
                'codigointerno': f"SN-{eq_data['nombre'][-3:]}",
                'anio': 2020,
                'activo': True
            }
        )
        equipos.append(equipo)
        if created:
            print(f"✅ Equipo creado: {equipo.nombreequipo}")
    
    # Crear estados de OT si no existen
    estado_abierta, _ = EstadosOrdenTrabajo.objects.get_or_create(
        nombreestadoot='Abierta',
        defaults={}
    )
    estado_progreso, _ = EstadosOrdenTrabajo.objects.get_or_create(
        nombreestadoot='En Progreso',
        defaults={}
    )
    estado_completada, _ = EstadosOrdenTrabajo.objects.get_or_create(
        nombreestadoot='Completada',
        defaults={}
    )
    
    # Crear tipos de mantenimiento si no existen
    tipo_preventivo, _ = TiposMantenimientoOT.objects.get_or_create(
        nombretipomantenimientoot='Preventivo',
        defaults={}
    )
    tipo_correctivo, _ = TiposMantenimientoOT.objects.get_or_create(
        nombretipomantenimientoot='Correctivo',
        defaults={}
    )
    
    # Crear órdenes para noviembre 2025
    ordenes_data = [
        {
            'fecha': datetime(2025, 11, 5),
            'equipo_idx': 0,
            'tipo': tipo_preventivo,
            'estado': estado_abierta,
            'prioridad': 'Media',
            'descripcion': 'Mantenimiento preventivo mensual - Revisión general del sistema'
        },
        {
            'fecha': datetime(2025, 11, 8),
            'equipo_idx': 1,
            'tipo': tipo_correctivo,
            'estado': estado_progreso,
            'prioridad': 'Alta',
            'descripcion': 'Reparación de sistema hidráulico - Fuga detectada'
        },
        {
            'fecha': datetime(2025, 11, 12),
            'equipo_idx': 2,
            'tipo': tipo_preventivo,
            'estado': estado_abierta,
            'prioridad': 'Media',
            'descripcion': 'Inspección de seguridad trimestral'
        },
        {
            'fecha': datetime(2025, 11, 15),
            'equipo_idx': 0,
            'tipo': tipo_preventivo,
            'estado': estado_abierta,
            'prioridad': 'Baja',
            'descripcion': 'Cambio de filtros de aire y aceite'
        },
        {
            'fecha': datetime(2025, 11, 18),
            'equipo_idx': 3,
            'tipo': tipo_correctivo,
            'estado': estado_abierta,
            'prioridad': 'Urgente',
            'descripcion': 'Falla en sistema eléctrico - Requiere atención inmediata'
        },
        {
            'fecha': datetime(2025, 11, 22),
            'equipo_idx': 4,
            'tipo': tipo_preventivo,
            'estado': estado_abierta,
            'prioridad': 'Media',
            'descripcion': 'Lubricación general y ajuste de componentes'
        },
        {
            'fecha': datetime(2025, 11, 25),
            'equipo_idx': 1,
            'tipo': tipo_preventivo,
            'estado': estado_completada,
            'prioridad': 'Media',
            'descripcion': 'Mantenimiento de neumáticos - Rotación y balanceo'
        },
        {
            'fecha': datetime(2025, 11, 28),
            'equipo_idx': 2,
            'tipo': tipo_correctivo,
            'estado': estado_abierta,
            'prioridad': 'Alta',
            'descripcion': 'Revisión de frenos - Desgaste excesivo detectado'
        },
    ]
    
    contador = 0
    for orden_data in ordenes_data:
        equipo = equipos[orden_data['equipo_idx']]
        
        # Generar número de OT
        numero_ot = f"OT-2025-11-{contador+1:03d}"
        
        # Verificar si ya existe
        if OrdenesTrabajo.objects.filter(numeroot=numero_ot).exists():
            print(f"⚠️  OT {numero_ot} ya existe")
            contador += 1
            continue
        
        # Crear la orden
        orden = OrdenesTrabajo.objects.create(
            numeroot=numero_ot,
            idequipo=equipo,
            idsolicitante=usuario,
            idtecnicoasignado=usuario,
            idestadoot=orden_data['estado'],
            idtipomantenimientoot=orden_data['tipo'],
            fechareportefalla=orden_data['fecha'],
            fechaejecucion=orden_data['fecha'],
            prioridad=orden_data['prioridad'],
            descripcionproblemareportado=orden_data['descripcion'],
            observacionesfinales=f"Orden creada para calendario de noviembre 2025"
        )
        
        print(f"✅ {numero_ot} - {equipo.nombreequipo} - {orden_data['fecha'].strftime('%d/%m/%Y')} - {orden_data['prioridad']}")
        contador += 1
    
    print(f"\n✅ Datos poblados exitosamente!")
    print(f"📦 Equipos: {Equipos.objects.count()}")
    print(f"📋 Órdenes de trabajo: {OrdenesTrabajo.objects.count()}")
    print(f"📅 Órdenes en noviembre 2025: {contador}")

if __name__ == '__main__':
    populate_all()
