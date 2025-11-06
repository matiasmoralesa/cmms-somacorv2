#!/usr/bin/env python
"""
Script para mostrar resumen de todos los datos generados
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import *
from django.contrib.auth.models import User

def mostrar_resumen():
    print("📊 RESUMEN COMPLETO DEL SISTEMA CMMS SOMACOR V2")
    print("=" * 60)
    
    # Contadores principales
    total_faenas = Faenas.objects.count()
    total_tipos_equipo = TiposEquipo.objects.count()
    total_equipos = Equipos.objects.count()
    total_usuarios_django = User.objects.count()
    total_usuarios_cmms = Usuarios.objects.count()
    total_ordenes = OrdenesTrabajo.objects.count()
    total_roles = Roles.objects.count()
    total_tipos_mantenimiento = TiposMantenimientoOT.objects.count()
    total_estados_ot = EstadosOrdenTrabajo.objects.count()
    
    print(f"\n🏢 ESTRUCTURA ORGANIZACIONAL:")
    print(f"   📍 Faenas: {total_faenas}")
    print(f"   👥 Roles: {total_roles}")
    print(f"   👤 Usuarios Django: {total_usuarios_django}")
    print(f"   👤 Perfiles CMMS: {total_usuarios_cmms}")
    
    print(f"\n🚜 EQUIPOS Y ACTIVOS:")
    print(f"   🔧 Tipos de Equipo: {total_tipos_equipo}")
    print(f"   🚜 Equipos Totales: {total_equipos}")
    print(f"   ✅ Equipos Activos: {Equipos.objects.filter(activo=True).count()}")
    print(f"   ❌ Equipos Inactivos: {Equipos.objects.filter(activo=False).count()}")
    
    print(f"\n📋 ÓRDENES DE TRABAJO:")
    print(f"   📊 Total Órdenes: {total_ordenes}")
    print(f"   🔧 Tipos Mantenimiento: {total_tipos_mantenimiento}")
    print(f"   📈 Estados OT: {total_estados_ot}")
    
    # Distribución por estado de órdenes
    print(f"\n📈 DISTRIBUCIÓN ÓRDENES POR ESTADO:")
    for estado in EstadosOrdenTrabajo.objects.all():
        count = OrdenesTrabajo.objects.filter(idestadoot=estado).count()
        porcentaje = (count / total_ordenes * 100) if total_ordenes > 0 else 0
        print(f"   📋 {estado.nombreestadoot}: {count} ({porcentaje:.1f}%)")
    
    # Distribución por tipo de mantenimiento
    print(f"\n🔧 DISTRIBUCIÓN POR TIPO MANTENIMIENTO:")
    for tipo in TiposMantenimientoOT.objects.all():
        count = OrdenesTrabajo.objects.filter(idtipomantenimientoot=tipo).count()
        porcentaje = (count / total_ordenes * 100) if total_ordenes > 0 else 0
        print(f"   🔧 {tipo.nombretipomantenimientoot}: {count} ({porcentaje:.1f}%)")
    
    # Distribución por prioridad
    print(f"\n⚡ DISTRIBUCIÓN POR PRIORIDAD:")
    for prioridad in ['Baja', 'Media', 'Alta', 'Crítica']:
        count = OrdenesTrabajo.objects.filter(prioridad=prioridad).count()
        porcentaje = (count / total_ordenes * 100) if total_ordenes > 0 else 0
        print(f"   ⚡ {prioridad}: {count} ({porcentaje:.1f}%)")
    
    # Top 5 equipos con más órdenes
    print(f"\n🏆 TOP 5 EQUIPOS CON MÁS ÓRDENES:")
    from django.db.models import Count
    top_equipos = Equipos.objects.annotate(
        num_ordenes=Count('ordenestrabajo')
    ).order_by('-num_ordenes')[:5]
    
    for i, equipo in enumerate(top_equipos, 1):
        print(f"   {i}. {equipo.nombreequipo}: {equipo.num_ordenes} órdenes")
    
    # Estadísticas temporales
    from django.utils import timezone
    from datetime import timedelta
    
    hoy = timezone.now()
    hace_30_dias = hoy - timedelta(days=30)
    hace_7_dias = hoy - timedelta(days=7)
    
    ordenes_mes = OrdenesTrabajo.objects.filter(fechacreacionot__gte=hace_30_dias).count()
    ordenes_semana = OrdenesTrabajo.objects.filter(fechacreacionot__gte=hace_7_dias).count()
    ordenes_completadas_mes = OrdenesTrabajo.objects.filter(
        fechacompletado__gte=hace_30_dias,
        idestadoot__nombreestadoot='Completada'
    ).count()
    
    print(f"\n📅 ESTADÍSTICAS TEMPORALES:")
    print(f"   📋 Órdenes últimos 30 días: {ordenes_mes}")
    print(f"   📋 Órdenes últimos 7 días: {ordenes_semana}")
    print(f"   ✅ Completadas último mes: {ordenes_completadas_mes}")
    
    # Total de registros en el sistema
    total_registros = (total_faenas + total_tipos_equipo + total_equipos + 
                      total_usuarios_django + total_usuarios_cmms + total_ordenes +
                      total_roles + total_tipos_mantenimiento + total_estados_ot)
    
    print(f"\n🎊 RESUMEN FINAL:")
    print(f"   📊 TOTAL REGISTROS PRINCIPALES: {total_registros}")
    print(f"   🎯 OBJETIVO CUMPLIDO: {'✅ SÍ' if total_registros >= 2000 else '❌ NO'}")
    
    if total_registros >= 2000:
        print(f"\n🎉 ¡FELICITACIONES!")
        print(f"   Se han generado {total_registros} registros en el sistema")
        print(f"   El sistema CMMS está listo para pruebas de rendimiento")
        print(f"   y demostración con datos realistas.")
    else:
        print(f"\n⚠️  OBJETIVO PARCIAL:")
        print(f"   Se generaron {total_registros} registros de {2000} objetivo")
        print(f"   Faltan {2000 - total_registros} registros para completar")
    
    print(f"\n🌐 URLs DEL SISTEMA:")
    print(f"   Frontend: http://localhost:5173")
    print(f"   Backend:  http://localhost:8000")
    print(f"   Admin:    http://localhost:8000/admin")
    
    print(f"\n🔑 CREDENCIALES:")
    print(f"   Usuario: admin")
    print(f"   Contraseña: admin123")

if __name__ == '__main__':
    mostrar_resumen()