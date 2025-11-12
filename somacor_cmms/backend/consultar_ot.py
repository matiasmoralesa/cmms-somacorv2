import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import OrdenesTrabajo
from django.db.models import Count

print("=" * 60)
print("ESTADÍSTICAS DE ÓRDENES DE TRABAJO")
print("=" * 60)

total = OrdenesTrabajo.objects.count()
print(f"\n📊 Total de Órdenes de Trabajo: {total}")

# Por estado
print("\n📋 Por Estado:")
estados = OrdenesTrabajo.objects.values('idestadoot__nombreestadoot').annotate(
    cantidad=Count('idordentrabajo')
).order_by('-cantidad')

for estado in estados:
    nombre_estado = estado['idestadoot__nombreestadoot'] or 'Sin estado'
    cantidad = estado['cantidad']
    print(f"   {nombre_estado}: {cantidad}")

# Por prioridad
print("\n⚠️  Por Prioridad:")
prioridades = OrdenesTrabajo.objects.values('prioridad').annotate(
    cantidad=Count('idordentrabajo')
).order_by('-cantidad')

for prioridad in prioridades:
    nombre_prioridad = prioridad['prioridad'] or 'Sin prioridad'
    cantidad = prioridad['cantidad']
    print(f"   {nombre_prioridad}: {cantidad}")

# Por tipo de mantenimiento
print("\n🔧 Por Tipo de Mantenimiento:")
tipos = OrdenesTrabajo.objects.values('idtipomantenimientoot__nombretipomantenimientoot').annotate(
    cantidad=Count('idordentrabajo')
).order_by('-cantidad')

for tipo in tipos:
    nombre_tipo = tipo['idtipomantenimientoot__nombretipomantenimientoot'] or 'Sin tipo'
    cantidad = tipo['cantidad']
    print(f"   {nombre_tipo}: {cantidad}")

# Últimas 5 órdenes creadas
print("\n📅 Últimas 5 Órdenes Creadas:")
ultimas = OrdenesTrabajo.objects.order_by('-fechareportefalla')[:5]

for ot in ultimas:
    print(f"   {ot.numeroot} - {ot.idequipo.nombreequipo if ot.idequipo else 'Sin equipo'} - {ot.fechareportefalla.strftime('%Y-%m-%d')}")

print("\n" + "=" * 60)
