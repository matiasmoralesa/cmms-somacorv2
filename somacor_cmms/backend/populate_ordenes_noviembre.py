"""
Script para crear órdenes de trabajo de prueba para noviembre 2025
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import OrdenesTrabajo, Equipos, EstadosOrdenTrabajo, TiposMantenimientoOT
from django.contrib.auth.models import User

def create_ordenes_noviembre():
    print("🔧 Creando órdenes de trabajo para noviembre 2025...")
    
    # Obtener datos necesarios
    usuario = User.objects.first()
    if not usuario:
        print("❌ No hay usuarios en el sistema")
        return
    
    equipos = list(Equipos.objects.all()[:5])
    if not equipos:
        print("❌ No hay equipos en el sistema")
        return
    
    estado_abierta = EstadosOrdenTrabajo.objects.filter(nombreestadoot='Abierta').first()
    estado_progreso = EstadosOrdenTrabajo.objects.filter(nombreestadoot='En Progreso').first()
    estado_completada = EstadosOrdenTrabajo.objects.filter(nombreestadoot='Completada').first()
    
    tipo_preventivo = TiposMantenimientoOT.objects.filter(nombretipomantenimientoot='Preventivo').first()
    tipo_correctivo = TiposMantenimientoOT.objects.filter(nombretipomantenimientoot='Correctivo').first()
    
    if not estado_abierta or not tipo_preventivo:
        print("❌ Faltan estados o tipos de mantenimiento")
        return
    
    # Crear órdenes para noviembre 2025
    ordenes_data = [
        {
            'fecha': datetime(2025, 11, 5),
            'equipo': equipos[0] if len(equipos) > 0 else None,
            'tipo': tipo_preventivo,
            'estado': estado_abierta,
            'prioridad': 'Media',
            'descripcion': 'Mantenimiento preventivo mensual - Revisión general'
        },
        {
            'fecha': datetime(2025, 11, 12),
            'equipo': equipos[1] if len(equipos) > 1 else equipos[0],
            'tipo': tipo_correctivo,
            'estado': estado_progreso or estado_abierta,
            'prioridad': 'Alta',
            'descripcion': 'Reparación de sistema hidráulico'
        },
        {
            'fecha': datetime(2025, 11, 15),
            'equipo': equipos[2] if len(equipos) > 2 else equipos[0],
            'tipo': tipo_preventivo,
            'estado': estado_abierta,
            'prioridad': 'Media',
            'descripcion': 'Inspección de seguridad trimestral'
        },
        {
            'fecha': datetime(2025, 11, 20),
            'equipo': equipos[3] if len(equipos) > 3 else equipos[0],
            'tipo': tipo_preventivo,
            'estado': estado_abierta,
            'prioridad': 'Baja',
            'descripcion': 'Cambio de filtros y lubricación'
        },
        {
            'fecha': datetime(2025, 11, 25),
            'equipo': equipos[4] if len(equipos) > 4 else equipos[0],
            'tipo': tipo_correctivo,
            'estado': estado_abierta,
            'prioridad': 'Urgente',
            'descripcion': 'Falla en sistema eléctrico - Requiere atención inmediata'
        },
        {
            'fecha': datetime(2025, 11, 28),
            'equipo': equipos[0] if len(equipos) > 0 else None,
            'tipo': tipo_preventivo,
            'estado': estado_completada or estado_abierta,
            'prioridad': 'Media',
            'descripcion': 'Mantenimiento de fin de mes'
        },
    ]
    
    contador = 0
    for orden_data in ordenes_data:
        if not orden_data['equipo']:
            continue
            
        # Generar número de OT
        numero_ot = f"OT-2025-11-{contador+1:03d}"
        
        # Verificar si ya existe
        if OrdenesTrabajo.objects.filter(numeroot=numero_ot).exists():
            print(f"⚠️  OT {numero_ot} ya existe, saltando...")
            continue
        
        # Crear la orden
        orden = OrdenesTrabajo.objects.create(
            numeroot=numero_ot,
            idequipo=orden_data['equipo'],
            idsolicitante=usuario,
            idtecnicoasignado=usuario,
            idestadoot=orden_data['estado'],
            idtipomantenimientoot=orden_data['tipo'],
            fechareportefalla=orden_data['fecha'],
            fechaprogramada=orden_data['fecha'],
            horaprogramada='08:00:00',
            prioridad=orden_data['prioridad'],
            descripcionproblemareportado=orden_data['descripcion'],
            observaciones=f"Orden creada para calendario de noviembre 2025"
        )
        
        print(f"✅ Creada: {numero_ot} - {orden_data['equipo'].nombreequipo} - {orden_data['fecha'].strftime('%d/%m/%Y')}")
        contador += 1
    
    print(f"\n✅ Se crearon {contador} órdenes de trabajo para noviembre 2025")
    print(f"📅 Total de órdenes en el sistema: {OrdenesTrabajo.objects.count()}")

if __name__ == '__main__':
    create_ordenes_noviembre()
