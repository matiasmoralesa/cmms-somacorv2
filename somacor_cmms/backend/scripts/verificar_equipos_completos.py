"""
Script para verificar que todos los equipos tengan características completas
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import Equipos, TiposEquipo, Faenas

print("\n" + "="*80)
print("VERIFICACIÓN DE CARACTERÍSTICAS COMPLETAS DE EQUIPOS")
print("="*80 + "\n")

equipos = Equipos.objects.all()
equipos_completos = 0
equipos_incompletos = 0

print("Verificando cada equipo...\n")

for equipo in equipos:
    campos_faltantes = []
    
    if not equipo.codigointerno:
        campos_faltantes.append("Código Interno")
    if not equipo.marca:
        campos_faltantes.append("Marca")
    if not equipo.modelo:
        campos_faltantes.append("Modelo")
    if not equipo.anio:
        campos_faltantes.append("Año")
    if not equipo.patente:
        campos_faltantes.append("Patente")
    if not equipo.idfaenaactual:
        campos_faltantes.append("Faena")
    
    if campos_faltantes:
        equipos_incompletos += 1
        print(f"❌ {equipo.nombreequipo}")
        print(f"   Campos faltantes: {', '.join(campos_faltantes)}")
        print()
    else:
        equipos_completos += 1
        print(f"✅ {equipo.codigointerno}: {equipo.nombreequipo}")
        print(f"   Marca: {equipo.marca} | Modelo: {equipo.modelo} | Año: {equipo.anio}")
        print(f"   Patente: {equipo.patente} | Faena: {equipo.idfaenaactual.nombrefaena}")
        print()

print("="*80)
print("RESUMEN DE VERIFICACIÓN")
print("="*80)
print(f"\n✅ Equipos completos: {equipos_completos}/{equipos.count()}")
print(f"❌ Equipos incompletos: {equipos_incompletos}/{equipos.count()}")

if equipos_incompletos == 0:
    print("\n🎉 ¡TODOS LOS EQUIPOS TIENEN CARACTERÍSTICAS COMPLETAS!")
else:
    print(f"\n⚠️  Hay {equipos_incompletos} equipos con información incompleta")

print("\n" + "="*80)
print("ESTADÍSTICAS ADICIONALES")
print("="*80 + "\n")

# Verificar distribución por tipo
print("Equipos por tipo:")
for tipo in TiposEquipo.objects.all():
    count = Equipos.objects.filter(idtipoequipo=tipo).count()
    print(f"  - {tipo.nombretipo}: {count}")

print("\nEquipos por faena:")
for faena in Faenas.objects.all():
    count = Equipos.objects.filter(idfaenaactual=faena).count()
    print(f"  - {faena.nombrefaena}: {count}")

print("\nMarcas únicas en el sistema:")
marcas = Equipos.objects.values_list('marca', flat=True).distinct().order_by('marca')
for marca in marcas:
    if marca:
        count = Equipos.objects.filter(marca=marca).count()
        print(f"  - {marca}: {count} equipos")

print("\nRango de años:")
anios = Equipos.objects.exclude(anio__isnull=True).values_list('anio', flat=True).order_by('anio')
if anios:
    print(f"  Desde {min(anios)} hasta {max(anios)}")

print("\n" + "="*80 + "\n")
