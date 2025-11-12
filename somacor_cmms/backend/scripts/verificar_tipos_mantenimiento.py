"""
Script para verificar que las órdenes de trabajo tengan tipos de mantenimiento asignados
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import OrdenesTrabajo, TiposMantenimientoOT

print("\n" + "="*80)
print("VERIFICACIÓN DE TIPOS DE MANTENIMIENTO EN ÓRDENES DE TRABAJO")
print("="*80 + "\n")

# Verificar tipos de mantenimiento disponibles
print("📋 Tipos de Mantenimiento Disponibles:")
tipos = TiposMantenimientoOT.objects.all()
for tipo in tipos:
    print(f"   - {tipo.nombretipomantenimientoot}")

print(f"\n   Total: {tipos.count()} tipos\n")

# Verificar órdenes de trabajo
ordenes = OrdenesTrabajo.objects.all()
print(f"🔧 Órdenes de Trabajo: {ordenes.count()} total\n")

# Contar órdenes con y sin tipo
con_tipo = ordenes.exclude(idtipomantenimientoot__isnull=True).count()
sin_tipo = ordenes.filter(idtipomantenimientoot__isnull=True).count()

print(f"✅ Con tipo asignado: {con_tipo}")
print(f"❌ Sin tipo asignado: {sin_tipo}\n")

# Mostrar distribución por tipo
if con_tipo > 0:
    print("📊 Distribución por Tipo de Mantenimiento:")
    for tipo in tipos:
        count = ordenes.filter(idtipomantenimientoot=tipo).count()
        if count > 0:
            porcentaje = (count / con_tipo) * 100
            barra = "█" * int(porcentaje / 5)
            print(f"   {tipo.nombretipomantenimientoot:20} {barra} {count:3} ({porcentaje:.1f}%)")

# Mostrar algunas órdenes de ejemplo
print(f"\n📝 Ejemplos de Órdenes de Trabajo (primeras 10):")
print("─" * 80)

for orden in ordenes[:10]:
    tipo_nombre = orden.idtipomantenimientoot.nombretipomantenimientoot if orden.idtipomantenimientoot else "N/A"
    estado_nombre = orden.idestadoot.nombreestadoot if orden.idestadoot else "N/A"
    equipo_nombre = orden.idequipo.nombreequipo if orden.idequipo else "N/A"
    
    print(f"\n{orden.numeroot}")
    print(f"   Equipo: {equipo_nombre}")
    print(f"   Tipo: {tipo_nombre}")
    print(f"   Estado: {estado_nombre}")
    print(f"   Descripción: {orden.descripcionproblemareportado[:50]}...")

print("\n" + "="*80)

if sin_tipo > 0:
    print(f"⚠️  ADVERTENCIA: Hay {sin_tipo} órdenes sin tipo de mantenimiento asignado")
    print("="*80 + "\n")
    
    # Asignar tipo por defecto si es necesario
    respuesta = input("¿Deseas asignar un tipo por defecto a las órdenes sin tipo? (s/n): ")
    
    if respuesta.lower() == 's':
        # Obtener o crear tipo "Correctivo" como predeterminado
        tipo_correctivo, created = TiposMantenimientoOT.objects.get_or_create(
            nombretipomantenimientoot='Correctivo',
            defaults={'descripcion': 'Mantenimiento correctivo'}
        )
        
        # Asignar a todas las órdenes sin tipo
        ordenes_sin_tipo = ordenes.filter(idtipomantenimientoot__isnull=True)
        count = ordenes_sin_tipo.update(idtipomantenimientoot=tipo_correctivo)
        
        print(f"\n✅ Se asignó el tipo 'Correctivo' a {count} órdenes")
        print("="*80 + "\n")
else:
    print("✅ TODAS LAS ÓRDENES TIENEN TIPO DE MANTENIMIENTO ASIGNADO")
    print("="*80 + "\n")
