"""
Script para mostrar un resumen visual completo de todos los equipos
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import Equipos, TiposEquipo, Faenas

def print_header(text, char="="):
    """Imprime un encabezado decorado"""
    print("\n" + char * 80)
    print(text.center(80))
    print(char * 80 + "\n")

def print_section(text):
    """Imprime una sección"""
    print("\n" + "─" * 80)
    print(f"  {text}")
    print("─" * 80)

print_header("📋 CATÁLOGO COMPLETO DE EQUIPOS", "═")

# Resumen general
total_equipos = Equipos.objects.count()
print(f"Total de equipos en el sistema: {total_equipos}")
print(f"Tipos de equipo: {TiposEquipo.objects.count()}")
print(f"Faenas activas: {Faenas.objects.count()}")

# Mostrar equipos por tipo
for tipo in TiposEquipo.objects.all().order_by('nombretipo'):
    equipos_tipo = Equipos.objects.filter(idtipoequipo=tipo).order_by('codigointerno')
    
    if equipos_tipo.count() == 0:
        continue
    
    print_section(f"🔧 {tipo.nombretipo.upper()} ({equipos_tipo.count()} equipos)")
    
    for equipo in equipos_tipo:
        print(f"\n  ┌─ {equipo.codigointerno} ─────────────────────────────────────")
        print(f"  │ 📌 Nombre:    {equipo.nombreequipo}")
        print(f"  │ 🏭 Marca:     {equipo.marca}")
        print(f"  │ 📦 Modelo:    {equipo.modelo}")
        print(f"  │ 📅 Año:       {equipo.anio}")
        print(f"  │ 🚗 Patente:   {equipo.patente}")
        print(f"  │ 📍 Faena:     {equipo.idfaenaactual.nombrefaena if equipo.idfaenaactual else 'Sin asignar'}")
        print(f"  │ ⚡ Estado:    {equipo.idestadoactual.nombreestado}")
        print(f"  └────────────────────────────────────────────────────────")

# Resumen por faena
print_header("📍 DISTRIBUCIÓN POR FAENA", "═")

for faena in Faenas.objects.all().order_by('nombrefaena'):
    equipos_faena = Equipos.objects.filter(idfaenaactual=faena)
    
    if equipos_faena.count() == 0:
        continue
    
    print_section(f"🏢 {faena.nombrefaena} ({equipos_faena.count()} equipos)")
    
    # Agrupar por tipo
    for tipo in TiposEquipo.objects.all():
        equipos_tipo_faena = equipos_faena.filter(idtipoequipo=tipo).order_by('codigointerno')
        
        if equipos_tipo_faena.count() > 0:
            print(f"\n  {tipo.nombretipo}:")
            for equipo in equipos_tipo_faena:
                print(f"    • {equipo.codigointerno:12} - {equipo.nombreequipo:35} [{equipo.patente}]")

# Estadísticas de marcas
print_header("🏭 ESTADÍSTICAS DE MARCAS", "═")

marcas = {}
for equipo in Equipos.objects.all():
    if equipo.marca:
        if equipo.marca not in marcas:
            marcas[equipo.marca] = []
        marcas[equipo.marca].append(equipo)

# Ordenar por cantidad
marcas_ordenadas = sorted(marcas.items(), key=lambda x: len(x[1]), reverse=True)

print("\nMarcas más utilizadas:")
for i, (marca, equipos_marca) in enumerate(marcas_ordenadas, 1):
    print(f"\n  {i}. {marca} ({len(equipos_marca)} equipos)")
    for equipo in equipos_marca:
        print(f"     • {equipo.codigointerno} - {equipo.modelo} ({equipo.anio})")

# Estadísticas de años
print_header("📅 ESTADÍSTICAS DE AÑOS", "═")

anios = {}
for equipo in Equipos.objects.exclude(anio__isnull=True):
    if equipo.anio not in anios:
        anios[equipo.anio] = 0
    anios[equipo.anio] += 1

print("\nDistribución por año de fabricación:")
for anio in sorted(anios.keys()):
    barra = "█" * anios[anio]
    print(f"  {anio}: {barra} ({anios[anio]} equipos)")

# Rango de años
anios_lista = sorted(anios.keys())
if anios_lista:
    print(f"\n  Rango: {anios_lista[0]} - {anios_lista[-1]}")
    print(f"  Edad promedio: {2024 - sum(anios_lista) / len(anios_lista):.1f} años")

# Resumen final
print_header("✅ RESUMEN FINAL", "═")

print("Estado de completitud de datos:")
print(f"  ✅ Equipos con código interno:  {Equipos.objects.exclude(codigointerno__isnull=True).count()}/{total_equipos}")
print(f"  ✅ Equipos con marca:           {Equipos.objects.exclude(marca__isnull=True).count()}/{total_equipos}")
print(f"  ✅ Equipos con modelo:          {Equipos.objects.exclude(modelo__isnull=True).count()}/{total_equipos}")
print(f"  ✅ Equipos con año:             {Equipos.objects.exclude(anio__isnull=True).count()}/{total_equipos}")
print(f"  ✅ Equipos con patente:         {Equipos.objects.exclude(patente__isnull=True).count()}/{total_equipos}")
print(f"  ✅ Equipos con faena:           {Equipos.objects.exclude(idfaenaactual__isnull=True).count()}/{total_equipos}")

# Verificar si todos están completos
equipos_completos = Equipos.objects.exclude(
    codigointerno__isnull=True
).exclude(
    marca__isnull=True
).exclude(
    modelo__isnull=True
).exclude(
    anio__isnull=True
).exclude(
    patente__isnull=True
).exclude(
    idfaenaactual__isnull=True
).count()

print(f"\n  🎉 Equipos 100% completos: {equipos_completos}/{total_equipos}")

if equipos_completos == total_equipos:
    print("\n" + "═" * 80)
    print("🎊 ¡PERFECTO! TODOS LOS EQUIPOS TIENEN INFORMACIÓN COMPLETA 🎊".center(80))
    print("═" * 80 + "\n")
else:
    print(f"\n  ⚠️  Faltan {total_equipos - equipos_completos} equipos por completar\n")
