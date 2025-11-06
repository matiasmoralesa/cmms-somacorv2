#!/usr/bin/env python
"""
Script para probar el dashboard directamente
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import *

def test_dashboard_data():
    print("🧪 Probando datos del dashboard directamente...")
    
    # Estadísticas de equipos
    total_equipos = Equipos.objects.count()
    equipos_activos = Equipos.objects.filter(activo=True).count()
    print(f"📊 Equipos - Total: {total_equipos}, Activos: {equipos_activos}")
    
    # Estadísticas de órdenes
    total_ordenes = OrdenesTrabajo.objects.count()
    ordenes_pendientes = OrdenesTrabajo.objects.filter(
        idestadoot__nombreestadoot__in=['Pendiente', 'Abierta', 'Asignada']
    ).count()
    ordenes_completadas = OrdenesTrabajo.objects.filter(
        idestadoot__nombreestadoot='Completada'
    ).count()
    
    print(f"📊 Órdenes - Total: {total_ordenes}, Pendientes: {ordenes_pendientes}, Completadas: {ordenes_completadas}")
    
    # Listar todas las órdenes
    print("\n📋 Órdenes existentes:")
    for orden in OrdenesTrabajo.objects.all():
        print(f"   - {orden.numeroot}: {orden.idestadoot.nombreestadoot} ({orden.prioridad})")
    
    # Listar todos los equipos
    print("\n🔧 Equipos existentes:")
    for equipo in Equipos.objects.all():
        print(f"   - {equipo.nombreequipo}: {equipo.idestadoactual.nombreestado} (Activo: {equipo.activo})")

if __name__ == '__main__':
    test_dashboard_data()