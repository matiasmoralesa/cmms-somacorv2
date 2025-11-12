#!/usr/bin/env python
"""
Script para generar equipos adicionales
"""
import os
import django
import sys
import random
from faker import Faker

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import *

fake = Faker('es_ES')

def generate_equipos():
    print("🚀 Generando equipos adicionales...")
    
    # Obtener datos existentes
    tipos_equipo = list(TiposEquipo.objects.all())
    estados_equipo = list(EstadosEquipo.objects.all())
    faenas = list(Faenas.objects.all())
    
    equipos_existentes = Equipos.objects.count()
    print(f"🚜 Equipos existentes: {equipos_existentes}")
    
    # Marcas y modelos realistas
    marcas_modelos = {
        'Caterpillar': ['320D', '330D', '336D', '349D', '950H', '962H', '972H', '980H'],
        'Komatsu': ['PC200', 'PC300', 'PC400', 'WA320', 'WA380', 'WA470', 'D65'],
        'Volvo': ['EC210', 'EC290', 'EC380', 'L120F', 'L150F', 'L220F', 'A30F'],
        'JCB': ['JS210', 'JS330', '3CX', '4CX', '540-170', '550-80', '560-80'],
        'Case': ['CX210', 'CX290', '580N', '695ST', '1150M', '1650L'],
        'Liebherr': ['R926', 'R936', 'R946', 'L556', 'L566', 'L576'],
        'Hitachi': ['ZX210', 'ZX290', 'ZX350', 'ZW220', 'ZW310'],
        'Doosan': ['DX225', 'DX300', 'DX380', 'DL250', 'DL300'],
        'Hyundai': ['HX220', 'HX300', 'HL757', 'HL760', 'HL770'],
        'Bobcat': ['E85', 'E145', 'S650', 'S750', 'S850', 'T650']
    }
    
    # Generar 150 equipos adicionales
    created_count = 0
    
    for i in range(1, 151):
        numero_equipo = equipos_existentes + i
        
        # Seleccionar marca y modelo
        marca = random.choice(list(marcas_modelos.keys()))
        modelo = random.choice(marcas_modelos[marca])
        tipo_equipo = random.choice(tipos_equipo)
        
        # Generar datos realistas
        anio = random.randint(2010, 2024)
        patente = fake.license_plate()[:6].replace('-', '').replace(' ', '')
        
        try:
            equipo = Equipos.objects.create(
                nombreequipo=f"{tipo_equipo.nombretipo} {marca} {modelo}-{numero_equipo:03d}",
                codigointerno=f"{marca[:3].upper()}-{numero_equipo:04d}",
                marca=marca,
                modelo=modelo,
                anio=anio,
                patente=patente,
                idtipoequipo=tipo_equipo,
                idestadoactual=random.choice(estados_equipo),
                idfaenaactual=random.choice(faenas),
                activo=random.choice([True, True, True, False])  # 75% activos
            )
            created_count += 1
            
            if i % 25 == 0:
                print(f"   🚜 Creados {i} equipos...")
                
        except Exception as e:
            print(f"❌ Error creando equipo {numero_equipo}: {e}")
    
    print(f"\n🎉 EQUIPOS ADICIONALES CREADOS!")
    print(f"📊 EQUIPOS CREADOS: {created_count}")
    print(f"📊 TOTAL EQUIPOS EN SISTEMA: {Equipos.objects.count()}")
    
    # Estadísticas por tipo
    print(f"\n🔧 DISTRIBUCIÓN POR TIPO:")
    for tipo in tipos_equipo:
        count = Equipos.objects.filter(idtipoequipo=tipo).count()
        print(f"   🔧 {tipo.nombretipo}: {count}")
    
    # Estadísticas por estado
    print(f"\n📈 DISTRIBUCIÓN POR ESTADO:")
    for estado in estados_equipo:
        count = Equipos.objects.filter(idestadoactual=estado).count()
        print(f"   📋 {estado.nombreestado}: {count}")

if __name__ == '__main__':
    generate_equipos()