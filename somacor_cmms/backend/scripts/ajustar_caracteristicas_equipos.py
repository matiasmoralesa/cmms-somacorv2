"""
Script para ajustar y completar TODAS las características de los equipos
Asegura datos realistas y completos para cada equipo
"""

import os
import sys
import django
from random import choice, randint

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import Equipos, TiposEquipo, Faenas, EstadosEquipo

print("\n" + "="*80)
print("AJUSTANDO CARACTERÍSTICAS COMPLETAS DE EQUIPOS")
print("="*80 + "\n")

# Datos realistas por tipo de equipo
DATOS_EQUIPOS = {
    'Camioneta': {
        'marcas': ['Toyota', 'Nissan', 'Mitsubishi', 'Ford', 'Chevrolet', 'Isuzu'],
        'modelos': {
            'Toyota': ['Hilux', 'Land Cruiser', 'Tacoma'],
            'Nissan': ['Frontier', 'Navara', 'Patrol'],
            'Mitsubishi': ['L200', 'Montero', 'Triton'],
            'Ford': ['Ranger', 'F-150', 'F-250'],
            'Chevrolet': ['Colorado', 'Silverado', 'S10'],
            'Isuzu': ['D-Max', 'MU-X']
        },
        'anios': list(range(2015, 2024)),
        'prefijo': 'CAM'
    },
    'Camionetas': {  # Variante plural
        'marcas': ['Toyota', 'Nissan', 'Mitsubishi', 'Ford', 'Chevrolet', 'Isuzu'],
        'modelos': {
            'Toyota': ['Hilux', 'Land Cruiser', 'Tacoma'],
            'Nissan': ['Frontier', 'Navara', 'Patrol'],
            'Mitsubishi': ['L200', 'Montero', 'Triton'],
            'Ford': ['Ranger', 'F-150', 'F-250'],
            'Chevrolet': ['Colorado', 'Silverado', 'S10'],
            'Isuzu': ['D-Max', 'MU-X']
        },
        'anios': list(range(2015, 2024)),
        'prefijo': 'CAM'
    },
    'Retroexcavadora': {
        'marcas': ['Caterpillar', 'JCB', 'Case', 'Komatsu', 'John Deere'],
        'modelos': {
            'Caterpillar': ['416F', '420F', '430F', '444F'],
            'JCB': ['3CX', '4CX', '5CX'],
            'Case': ['580N', '590', '695'],
            'Komatsu': ['WB93R', 'WB97R', 'WB150'],
            'John Deere': ['310L', '410L', '710L']
        },
        'anios': list(range(2012, 2023)),
        'prefijo': 'RETRO'
    },
    'Cargador Frontal': {
        'marcas': ['Caterpillar', 'Komatsu', 'Volvo', 'John Deere', 'Case'],
        'modelos': {
            'Caterpillar': ['950M', '962M', '966M', '972M'],
            'Komatsu': ['WA320', 'WA380', 'WA470', 'WA500'],
            'Volvo': ['L90H', 'L110H', 'L120H', 'L150H'],
            'John Deere': ['544K', '624K', '644K', '724K'],
            'Case': ['621F', '721F', '821F', '921F']
        },
        'anios': list(range(2013, 2023)),
        'prefijo': 'CARG'
    },
    'Minicargador': {
        'marcas': ['Bobcat', 'Caterpillar', 'Case', 'John Deere', 'Gehl'],
        'modelos': {
            'Bobcat': ['S570', 'S590', 'S650', 'S770'],
            'Caterpillar': ['236D', '246D', '262D', '272D'],
            'Case': ['SR175', 'SR200', 'SR250', 'SR270'],
            'John Deere': ['318E', '320E', '326E', '332E'],
            'Gehl': ['R165', 'R190', 'R220', 'R260']
        },
        'anios': list(range(2014, 2024)),
        'prefijo': 'MINI'
    },
    'Camión Supersucker': {
        'marcas': ['Freightliner', 'Kenworth', 'Peterbilt', 'International'],
        'modelos': {
            'Freightliner': ['M2 106', 'M2 112', 'Cascadia'],
            'Kenworth': ['T370', 'T440', 'T470'],
            'Peterbilt': ['337', '348', '367'],
            'International': ['DuraStar', 'WorkStar']
        },
        'anios': list(range(2016, 2023)),
        'prefijo': 'SUPER'
    },
    'Camion Supersucker': {  # Variante sin tilde
        'marcas': ['Freightliner', 'Kenworth', 'Peterbilt', 'International'],
        'modelos': {
            'Freightliner': ['M2 106', 'M2 112', 'Cascadia'],
            'Kenworth': ['T370', 'T440', 'T470'],
            'Peterbilt': ['337', '348', '367'],
            'International': ['DuraStar', 'WorkStar']
        },
        'anios': list(range(2016, 2023)),
        'prefijo': 'SUPER'
    }
}

def generar_patente():
    """Genera una patente chilena realista"""
    # Formato antiguo: AA-1234 o Formato nuevo: BBBB-12
    if randint(0, 1):
        # Formato antiguo
        letras = ''.join([choice('ABCDEFGHJKLMNPRSTUVWXYZ') for _ in range(2)])
        numeros = ''.join([str(randint(0, 9)) for _ in range(4)])
        return f"{letras}-{numeros}"
    else:
        # Formato nuevo
        letras = ''.join([choice('BCDFGHJKLPRSTVWXYZ') for _ in range(4)])
        numeros = ''.join([str(randint(0, 9)) for _ in range(2)])
        return f"{letras}-{numeros}"

# Obtener todos los tipos de equipo
tipos_equipo = {tipo.nombretipo: tipo for tipo in TiposEquipo.objects.all()}
faenas = list(Faenas.objects.all())
estado_operativo = EstadosEquipo.objects.get(nombreestado='Operativo')

print("1. Ajustando características de equipos existentes...\n")

equipos_actualizados = 0
patentes_usadas = set()

for equipo in Equipos.objects.all():
    tipo_nombre = equipo.idtipoequipo.nombretipo
    
    if tipo_nombre not in DATOS_EQUIPOS:
        print(f"   ⚠️  Tipo '{tipo_nombre}' no tiene datos configurados, saltando...")
        continue
    
    datos = DATOS_EQUIPOS[tipo_nombre]
    
    # Seleccionar marca y modelo
    marca = choice(datos['marcas'])
    modelo = choice(datos['modelos'][marca])
    anio = choice(datos['anios'])
    
    # Generar patente única
    patente = generar_patente()
    while patente in patentes_usadas:
        patente = generar_patente()
    patentes_usadas.add(patente)
    
    # Generar código interno si no tiene
    if not equipo.codigointerno:
        contador = Equipos.objects.filter(
            idtipoequipo=equipo.idtipoequipo
        ).count()
        equipo.codigointerno = f"{datos['prefijo']}-{contador:03d}"
    
    # Actualizar equipo
    equipo.marca = marca
    equipo.modelo = modelo
    equipo.anio = anio
    equipo.patente = patente
    equipo.nombreequipo = f"{marca} {modelo} {anio}"
    
    # Asignar faena si no tiene
    if not equipo.idfaenaactual:
        equipo.idfaenaactual = choice(faenas)
    
    # Asegurar estado operativo
    equipo.idestadoactual = estado_operativo
    equipo.activo = True
    
    equipo.save()
    equipos_actualizados += 1
    
    print(f"   ✅ {equipo.codigointerno}: {equipo.nombreequipo}")
    print(f"      Patente: {equipo.patente}")
    print(f"      Faena: {equipo.idfaenaactual.nombrefaena}")
    print()

print(f"\n✅ {equipos_actualizados} equipos actualizados con características completas\n")

# 2. Resumen por tipo de equipo
print("="*80)
print("RESUMEN POR TIPO DE EQUIPO")
print("="*80 + "\n")

for tipo in TiposEquipo.objects.all():
    equipos_tipo = Equipos.objects.filter(idtipoequipo=tipo)
    print(f"\n{tipo.nombretipo}: {equipos_tipo.count()} equipos")
    print("-" * 60)
    
    for equipo in equipos_tipo:
        print(f"  {equipo.codigointerno:12} | {equipo.nombreequipo:30} | {equipo.patente:10}")
        print(f"  {'':12} | Faena: {equipo.idfaenaactual.nombrefaena if equipo.idfaenaactual else 'Sin asignar'}")
        print()

# 3. Resumen por faena
print("\n" + "="*80)
print("RESUMEN POR FAENA")
print("="*80 + "\n")

for faena in faenas:
    equipos_faena = Equipos.objects.filter(idfaenaactual=faena)
    print(f"\n{faena.nombrefaena}: {equipos_faena.count()} equipos")
    print("-" * 60)
    
    # Agrupar por tipo
    for tipo in TiposEquipo.objects.all():
        count = equipos_faena.filter(idtipoequipo=tipo).count()
        if count > 0:
            print(f"  - {tipo.nombretipo}: {count}")

print("\n" + "="*80)
print("✅ COMPLETADO - Todas las características ajustadas correctamente")
print("="*80 + "\n")
