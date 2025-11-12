"""
Script para verificar que las métricas de los equipos se calculen correctamente
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import Equipos, OrdenesTrabajo
from django.utils import timezone

print("\n" + "="*80)
print("VERIFICACIÓN DE MÉTRICAS DE EQUIPOS")
print("="*80 + "\n")

# Seleccionar algunos equipos para verificar
equipos = Equipos.objects.all()[:5]

for equipo in equipos:
    print(f"\n{'─'*80}")
    print(f"📦 EQUIPO: {equipo.nombreequipo} ({equipo.codigointerno})")
    print(f"{'─'*80}")
    
    # Información básica
    print(f"\n📋 Información Básica:")
    print(f"   Marca: {equipo.marca}")
    print(f"   Modelo: {equipo.modelo}")
    print(f"   Patente: {equipo.patente}")
    print(f"   Tipo: {equipo.idtipoequipo.nombretipo if equipo.idtipoequipo else 'N/A'}")
    print(f"   Estado: {equipo.idestadoactual.nombreestado if equipo.idestadoactual else 'N/A'}")
    print(f"   Faena: {equipo.idfaenaactual.nombrefaena if equipo.idfaenaactual else 'N/A'}")
    
    # Órdenes de trabajo
    ordenes = OrdenesTrabajo.objects.filter(idequipo=equipo)
    ordenes_30_dias = ordenes.filter(
        fechareportefalla__gte=timezone.now() - timedelta(days=30)
    )
    
    total_ordenes = ordenes.count()
    ordenes_completadas = ordenes.filter(
        idestadoot__nombreestadoot='Completada'
    ).count()
    ordenes_pendientes = ordenes.filter(
        idestadoot__nombreestadoot__in=['Abierta', 'Asignada', 'En Progreso']
    ).count()
    
    print(f"\n🔧 Órdenes de Trabajo:")
    print(f"   Total de órdenes: {total_ordenes}")
    print(f"   Completadas: {ordenes_completadas}")
    print(f"   Pendientes: {ordenes_pendientes}")
    print(f"   Últimos 30 días: {ordenes_30_dias.count()}")
    
    # Calcular horas de mantenimiento
    ordenes_mantenimiento = ordenes_30_dias.filter(
        idtipomantenimientoot__isnull=False
    )
    
    horas_mantenimiento = 0
    for orden in ordenes_mantenimiento:
        if orden.fechacompletado and orden.fechareportefalla:
            delta = orden.fechacompletado - orden.fechareportefalla
            horas_mantenimiento += delta.total_seconds() / 3600
    
    print(f"   Horas de mantenimiento (30 días): {horas_mantenimiento:.1f}h")
    
    # Calcular métricas
    estado_nombre = equipo.idestadoactual.nombreestado if equipo.idestadoactual else 'Desconocido'
    
    # Calcular uptime
    dias_totales = 30
    horas_totales = dias_totales * 24
    porcentaje_inactividad = (horas_mantenimiento / horas_totales) * 100 if horas_totales > 0 else 0
    uptime = max(0, min(100, 100 - porcentaje_inactividad))
    
    # Ajustar según estado
    if 'operativo' in estado_nombre.lower():
        uptime = max(uptime, 95)
        efficiency = 92
        availability = 100
        health_score = 95
    elif 'mantenimiento' in estado_nombre.lower():
        uptime = min(uptime, 80)
        efficiency = 60
        availability = 0
        health_score = 65
    else:
        uptime = min(uptime, 50)
        efficiency = 20
        availability = 0
        health_score = 25
    
    # Ajustar health_score basado en órdenes pendientes
    if ordenes_pendientes > 0:
        health_score = max(25, health_score - (ordenes_pendientes * 10))
    
    # Ajustar efficiency basado en órdenes completadas
    if total_ordenes > 0:
        tasa_completado = (ordenes_completadas / total_ordenes) * 100
        efficiency = min(efficiency, tasa_completado)
    
    # Calcular OEE
    oee_score = (availability * efficiency * (health_score / 100)) / 100
    
    print(f"\n📊 Métricas Calculadas:")
    print(f"   Health Score: {health_score:.1f}%")
    print(f"   Uptime: {uptime:.1f}%")
    print(f"   Efficiency: {efficiency:.1f}%")
    print(f"   Availability: {availability:.1f}%")
    print(f"   OEE Score: {oee_score:.1f}%")
    
    # Último mantenimiento
    ultimo_mantenimiento = ordenes.filter(
        idestadoot__nombreestadoot='Completada',
        idtipomantenimientoot__isnull=False
    ).order_by('-fechacompletado').first()
    
    if ultimo_mantenimiento and ultimo_mantenimiento.fechacompletado:
        dias_desde = (timezone.now() - ultimo_mantenimiento.fechacompletado).days
        print(f"\n📅 Mantenimiento:")
        print(f"   Último mantenimiento: {ultimo_mantenimiento.fechacompletado.strftime('%d-%m-%Y')}")
        print(f"   Días desde último: {dias_desde}")
        
        proximo = ultimo_mantenimiento.fechacompletado + timedelta(days=30)
        print(f"   Próximo mantenimiento: {proximo.strftime('%d-%m-%Y')}")
    else:
        print(f"\n📅 Mantenimiento:")
        print(f"   Sin registros de mantenimiento")
    
    # Fallas
    print(f"\n⚠️  Fallas:")
    print(f"   Fallas activas: {ordenes_pendientes}")
    print(f"   Fallas (30 días): {ordenes_30_dias.count()}")

print("\n" + "="*80)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*80 + "\n")

print("💡 Notas:")
print("   - Health Score se ajusta según órdenes pendientes")
print("   - Uptime se calcula basado en horas de mantenimiento")
print("   - Efficiency se ajusta según tasa de completado")
print("   - OEE = (Availability × Efficiency × Health) / 100")
print()
