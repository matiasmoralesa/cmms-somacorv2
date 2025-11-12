"""
Script para inicializar los 5 tipos de equipos del proyecto CMMS Somacor
Basado en los checklists proporcionados en PDF
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'somacor_cmms.settings')
django.setup()

from equipos.models import TipoEquipo, Equipo
from django.contrib.auth import get_user_model

User = get_user_model()

def crear_tipos_equipo():
    """Crear los 5 tipos de equipos del proyecto"""
    
    tipos_equipo = [
        {
            'nombre': 'Camionetas',
            'categoria': 'Vehículos Livianos',
            'descripcion': 'Vehículos de transporte liviano para personal y materiales',
            'codigo_checklist': 'F-PR-020-CH01',
            'frecuencia_mantenimiento': 5000,  # km
            'unidad_medida': 'km'
        },
        {
            'nombre': 'Retroexcavadora',
            'categoria': 'Maquinaria Pesada',
            'descripcion': 'Equipo de excavación y movimiento de tierra',
            'codigo_checklist': 'F-PR-034-CH01',
            'frecuencia_mantenimiento': 250,  # horas
            'unidad_medida': 'horas'
        },
        {
            'nombre': 'Cargador Frontal',
            'categoria': 'Maquinaria Pesada',
            'descripcion': 'Equipo de carga de materiales',
            'codigo_checklist': 'F-PR-037-CH01',
            'frecuencia_mantenimiento': 250,  # horas
            'unidad_medida': 'horas'
        },
        {
            'nombre': 'Minicargador',
            'categoria': 'Maquinaria Compacta',
            'descripcion': 'Equipo compacto de carga para espacios reducidos',
            'codigo_checklist': 'F-PR-040-CH01',
            'frecuencia_mantenimiento': 200,  # horas
            'unidad_medida': 'horas'
        },
        {
            'nombre': 'Camión Supersucker',
            'categoria': 'Vehículos Especializados',
            'descripcion': 'Camión de succión industrial para limpieza',
            'codigo_checklist': 'SUPERSUCKER-01',
            'frecuencia_mantenimiento': 10000,  # km
            'unidad_medida': 'km'
        }
    ]
    
    print("=" * 80)
    print("CREANDO TIPOS DE EQUIPO")
    print("=" * 80)
    
    tipos_creados = []
    
    for tipo_data in tipos_equipo:
        tipo, created = TipoEquipo.objects.get_or_create(
            nombre=tipo_data['nombre'],
            defaults={
                'descripcion': tipo_data['descripcion'],
                'activo': True
            }
        )
        
        if created:
            print(f"✅ Creado: {tipo.nombre} ({tipo_data['categoria']})")
        else:
            print(f"ℹ️  Ya existe: {tipo.nombre}")
        
        tipos_creados.append(tipo)
    
    print(f"\n✅ Total tipos de equipo: {len(tipos_creados)}")
    return tipos_creados


def crear_equipos_ejemplo(tipos_equipo):
    """Crear equipos de ejemplo para cada tipo"""
    
    print("\n" + "=" * 80)
    print("CREANDO EQUIPOS DE EJEMPLO")
    print("=" * 80)
    
    equipos_data = [
        # Camionetas
        {
            'tipo': 'Camionetas',
            'codigo': 'CAM-001',
            'nombre': 'Camioneta Toyota Hilux 2020',
            'marca': 'Toyota',
            'modelo': 'Hilux',
            'año': 2020,
            'ubicacion': 'Faena Central',
            'horometro_inicial': 45000
        },
        {
            'tipo': 'Camionetas',
            'codigo': 'CAM-002',
            'nombre': 'Camioneta Ford Ranger 2021',
            'marca': 'Ford',
            'modelo': 'Ranger',
            'año': 2021,
            'ubicacion': 'Faena Norte',
            'horometro_inicial': 32000
        },
        
        # Retroexcavadoras
        {
            'tipo': 'Retroexcavadora',
            'codigo': 'RETRO-001',
            'nombre': 'Retroexcavadora CAT 420F',
            'marca': 'Caterpillar',
            'modelo': '420F',
            'año': 2019,
            'ubicacion': 'Faena Central',
            'horometro_inicial': 3500
        },
        {
            'tipo': 'Retroexcavadora',
            'codigo': 'RETRO-002',
            'nombre': 'Retroexcavadora JCB 3CX',
            'marca': 'JCB',
            'modelo': '3CX',
            'año': 2020,
            'ubicacion': 'Faena Sur',
            'horometro_inicial': 2800
        },
        
        # Cargadores Frontales
        {
            'tipo': 'Cargador Frontal',
            'codigo': 'CARG-001',
            'nombre': 'Cargador Frontal CAT 950M',
            'marca': 'Caterpillar',
            'modelo': '950M',
            'año': 2018,
            'ubicacion': 'Faena Central',
            'horometro_inicial': 5200
        },
        {
            'tipo': 'Cargador Frontal',
            'codigo': 'CARG-002',
            'nombre': 'Cargador Frontal Komatsu WA380',
            'marca': 'Komatsu',
            'modelo': 'WA380',
            'año': 2019,
            'ubicacion': 'Faena Norte',
            'horometro_inicial': 4100
        },
        
        # Minicargadores
        {
            'tipo': 'Minicargador',
            'codigo': 'MINI-001',
            'nombre': 'Minicargador Bobcat S650',
            'marca': 'Bobcat',
            'modelo': 'S650',
            'año': 2020,
            'ubicacion': 'Faena Central',
            'horometro_inicial': 1800
        },
        {
            'tipo': 'Minicargador',
            'codigo': 'MINI-002',
            'nombre': 'Minicargador CAT 262D',
            'marca': 'Caterpillar',
            'modelo': '262D',
            'año': 2021,
            'ubicacion': 'Faena Sur',
            'horometro_inicial': 950
        },
        
        # Camiones Supersucker
        {
            'tipo': 'Camión Supersucker',
            'codigo': 'SUPER-001',
            'nombre': 'Camión Supersucker Volvo FMX',
            'marca': 'Volvo',
            'modelo': 'FMX 500',
            'año': 2019,
            'ubicacion': 'Faena Central',
            'horometro_inicial': 78000
        },
        {
            'tipo': 'Camión Supersucker',
            'codigo': 'SUPER-002',
            'nombre': 'Camión Supersucker Mercedes Actros',
            'marca': 'Mercedes-Benz',
            'modelo': 'Actros 2646',
            'año': 2020,
            'ubicacion': 'Faena Norte',
            'horometro_inicial': 52000
        }
    ]
    
    equipos_creados = []
    
    for equipo_data in equipos_data:
        # Buscar el tipo de equipo
        tipo = next((t for t in tipos_equipo if t.nombre == equipo_data['tipo']), None)
        
        if not tipo:
            print(f"❌ Tipo de equipo no encontrado: {equipo_data['tipo']}")
            continue
        
        equipo, created = Equipo.objects.get_or_create(
            codigointerno=equipo_data['codigo'],
            defaults={
                'nombreequipo': equipo_data['nombre'],
                'idtipoequipo': tipo,
                'marca': equipo_data['marca'],
                'modelo': equipo_data['modelo'],
                'anofabricacion': equipo_data['año'],
                'ubicacion': equipo_data['ubicacion'],
                'horometro': equipo_data['horometro_inicial'],
                'estado': 'Operativo',
                'activo': True
            }
        )
        
        if created:
            print(f"✅ Creado: {equipo.codigointerno} - {equipo.nombreequipo}")
        else:
            print(f"ℹ️  Ya existe: {equipo.codigointerno}")
        
        equipos_creados.append(equipo)
    
    print(f"\n✅ Total equipos creados: {len(equipos_creados)}")
    return equipos_creados


def mostrar_resumen(tipos_equipo, equipos):
    """Mostrar resumen de la inicialización"""
    
    print("\n" + "=" * 80)
    print("RESUMEN DE INICIALIZACIÓN")
    print("=" * 80)
    
    print(f"\n📊 Tipos de Equipo: {len(tipos_equipo)}")
    for tipo in tipos_equipo:
        count = Equipo.objects.filter(idtipoequipo=tipo).count()
        print(f"   - {tipo.nombre}: {count} equipos")
    
    print(f"\n🚜 Total Equipos: {len(equipos)}")
    
    print("\n📋 Equipos por Ubicación:")
    ubicaciones = Equipo.objects.values_list('ubicacion', flat=True).distinct()
    for ubicacion in ubicaciones:
        count = Equipo.objects.filter(ubicacion=ubicacion).count()
        print(f"   - {ubicacion}: {count} equipos")
    
    print("\n" + "=" * 80)
    print("✅ INICIALIZACIÓN COMPLETADA")
    print("=" * 80)


def main():
    """Función principal"""
    
    print("\n" + "=" * 80)
    print("INICIALIZACIÓN DE EQUIPOS DEL PROYECTO CMMS SOMACOR")
    print("=" * 80)
    print("\nBasado en los 5 checklists proporcionados:")
    print("  1. F-PR-020-CH01 - Camionetas")
    print("  2. F-PR-034-CH01 - Retroexcavadora")
    print("  3. F-PR-037-CH01 - Cargador Frontal")
    print("  4. F-PR-040-CH01 - Minicargador")
    print("  5. Check List Camión Supersucker")
    print("\n" + "=" * 80)
    
    try:
        # Crear tipos de equipo
        tipos_equipo = crear_tipos_equipo()
        
        # Crear equipos de ejemplo
        equipos = crear_equipos_ejemplo(tipos_equipo)
        
        # Mostrar resumen
        mostrar_resumen(tipos_equipo, equipos)
        
        print("\n✅ Script ejecutado exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
