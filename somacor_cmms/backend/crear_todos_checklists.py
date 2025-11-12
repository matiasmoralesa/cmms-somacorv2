"""
Script para crear templates de checklist para TODOS los tipos de equipo
Basado en los PDFs del proyecto
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import ChecklistTemplate, ChecklistCategory, ChecklistItem, TiposEquipo

def crear_template_completo(tipo_nombre, template_nombre, categorias_items):
    """
    Crea un template completo con sus categorías e items
    """
    try:
        tipo = TiposEquipo.objects.get(nombretipo=tipo_nombre)
    except TiposEquipo.DoesNotExist:
        print(f"❌ Tipo de equipo '{tipo_nombre}' no existe")
        return False
    
    # Verificar si ya existe
    if ChecklistTemplate.objects.filter(tipo_equipo=tipo).exists():
        print(f"⏭️  Ya existe template para {tipo_nombre}")
        return True
    
    # Crear template
    template = ChecklistTemplate.objects.create(
        nombre=template_nombre,
        tipo_equipo=tipo,
        activo=True
    )
    print(f"✅ Template creado: {template_nombre}")
    
    # Crear categorías e items
    total_items = 0
    for orden_cat, (cat_nombre, items) in enumerate(categorias_items, 1):
        categoria = ChecklistCategory.objects.create(
            template=template,
            nombre=cat_nombre,
            orden=orden_cat
        )
        
        for orden_item, (item_texto, es_critico) in enumerate(items, 1):
            ChecklistItem.objects.create(
                category=categoria,
                texto=item_texto,
                es_critico=es_critico,
                orden=orden_item
            )
            total_items += 1
    
    print(f"   📋 {len(categorias_items)} categorías con {total_items} items")
    return True

def main():
    print("=" * 70)
    print("CREANDO TEMPLATES DE CHECKLIST PARA TODOS LOS TIPOS DE EQUIPO")
    print("=" * 70)
    
    # 1. CAMIÓN SUPERSUCKER
    crear_template_completo(
        "Camion Supersucker",
        "Checklist Diario - Camión Supersucker",
        [
            ("MOTOR Y SISTEMA DE COMBUSTIBLE", [
                ("Nivel de aceite del motor", True),
                ("Fugas de aceite del motor", True),
                ("Nivel de refrigerante", True),
                ("Fugas de refrigerante", True),
                ("Nivel de combustible", False),
                ("Fugas de combustible", True),
                ("Filtro de aire", False),
                ("Correas y mangueras", False),
            ]),
            ("SISTEMA HIDRÁULICO", [
                ("Nivel de aceite hidráulico", True),
                ("Fugas de aceite hidráulico", True),
                ("Mangueras hidráulicas", False),
                ("Bomba de vacío", True),
                ("Tanque de agua", False),
                ("Sistema de succión", True),
            ]),
            ("SISTEMA ELÉCTRICO", [
                ("Batería y terminales", False),
                ("Luces delanteras", True),
                ("Luces traseras", True),
                ("Luces de emergencia", True),
                ("Bocina", False),
                ("Instrumentos del tablero", False),
            ]),
            ("SEGURIDAD", [
                ("Cinturón de seguridad", True),
                ("Espejos retrovisores", True),
                ("Extintor", True),
                ("Botiquín", False),
                ("Conos de seguridad", False),
                ("Alarma de retroceso", True),
            ]),
            ("NEUMÁTICOS Y FRENOS", [
                ("Presión de neumáticos", True),
                ("Estado de neumáticos", True),
                ("Freno de servicio", True),
                ("Freno de estacionamiento", True),
                ("Nivel de líquido de frenos", True),
            ]),
        ]
    )
    
    # 2. CAMIONETAS
    crear_template_completo(
        "Camionetas",
        "Checklist Diario - Camionetas",
        [
            ("MOTOR", [
                ("Nivel de aceite", True),
                ("Nivel de refrigerante", True),
                ("Nivel de combustible", False),
                ("Fugas visibles", True),
                ("Correas", False),
            ]),
            ("LUCES Y SEÑALIZACIÓN", [
                ("Luces delanteras", True),
                ("Luces traseras", True),
                ("Luces de freno", True),
                ("Intermitentes", True),
                ("Luces de emergencia", True),
            ]),
            ("SEGURIDAD", [
                ("Cinturones de seguridad", True),
                ("Espejos", True),
                ("Limpiaparabrisas", False),
                ("Bocina", False),
                ("Extintor", True),
            ]),
            ("NEUMÁTICOS", [
                ("Presión neumático delantero izquierdo", True),
                ("Presión neumático delantero derecho", True),
                ("Presión neumático trasero izquierdo", True),
                ("Presión neumático trasero derecho", True),
                ("Estado general de neumáticos", True),
            ]),
            ("FRENOS", [
                ("Freno de servicio", True),
                ("Freno de estacionamiento", True),
                ("Nivel de líquido de frenos", True),
            ]),
            ("DOCUMENTACIÓN", [
                ("Licencia de conducir vigente", True),
                ("Revisión técnica vigente", True),
                ("Seguro obligatorio vigente", True),
                ("Permiso de circulación", True),
            ]),
        ]
    )
    
    # 3. RETROEXCAVADORA
    crear_template_completo(
        "Retroexcavadora",
        "Checklist Diario - Retroexcavadora",
        [
            ("MOTOR", [
                ("Nivel de aceite del motor", True),
                ("Nivel de refrigerante", True),
                ("Nivel de combustible", False),
                ("Fugas de aceite", True),
                ("Filtro de aire", False),
            ]),
            ("SISTEMA HIDRÁULICO", [
                ("Nivel de aceite hidráulico", True),
                ("Fugas de aceite hidráulico", True),
                ("Cilindros hidráulicos", False),
                ("Mangueras hidráulicas", False),
                ("Brazo excavador", False),
                ("Cuchara retroexcavadora", False),
            ]),
            ("SISTEMA ELÉCTRICO", [
                ("Batería", False),
                ("Luces de trabajo", True),
                ("Luces de emergencia", True),
                ("Bocina", False),
                ("Instrumentos", False),
            ]),
            ("SEGURIDAD", [
                ("Cinturón de seguridad", True),
                ("Alarma de retroceso", True),
                ("Extintor", True),
                ("Espejos", True),
                ("Cabina (vidrios, puertas)", False),
            ]),
            ("TREN DE RODAJE", [
                ("Neumáticos delanteros", True),
                ("Neumáticos traseros", True),
                ("Freno de servicio", True),
                ("Freno de estacionamiento", True),
            ]),
            ("IMPLEMENTOS", [
                ("Cuchara frontal", False),
                ("Brazo retroexcavador", False),
                ("Estabilizadores", True),
                ("Pasadores y seguros", True),
            ]),
        ]
    )
    
    # 4. CARGADOR FRONTAL
    crear_template_completo(
        "Cargador Frontal",
        "Checklist Diario - Cargador Frontal",
        [
            ("MOTOR", [
                ("Nivel de aceite del motor", True),
                ("Nivel de refrigerante", True),
                ("Nivel de combustible", False),
                ("Fugas visibles", True),
                ("Filtro de aire", False),
            ]),
            ("SISTEMA HIDRÁULICO", [
                ("Nivel de aceite hidráulico", True),
                ("Fugas de aceite hidráulico", True),
                ("Cilindros de levante", False),
                ("Cilindros de volteo", False),
                ("Mangueras hidráulicas", False),
            ]),
            ("SISTEMA ELÉCTRICO", [
                ("Batería y terminales", False),
                ("Luces de trabajo", True),
                ("Luces de emergencia", True),
                ("Bocina", False),
                ("Instrumentos del tablero", False),
            ]),
            ("SEGURIDAD", [
                ("Cinturón de seguridad", True),
                ("Alarma de retroceso", True),
                ("Extintor", True),
                ("Espejos retrovisores", True),
                ("Cabina (estructura ROPS)", True),
            ]),
            ("NEUMÁTICOS Y FRENOS", [
                ("Neumáticos delanteros", True),
                ("Neumáticos traseros", True),
                ("Presión de neumáticos", True),
                ("Freno de servicio", True),
                ("Freno de estacionamiento", True),
            ]),
            ("IMPLEMENTOS", [
                ("Cuchara cargadora", False),
                ("Pasadores de cuchara", True),
                ("Dientes de cuchara", False),
                ("Sistema de volteo", False),
            ]),
        ]
    )
    
    # 5. MINICARGADOR
    crear_template_completo(
        "Minicargador",
        "Checklist Diario - Minicargador",
        [
            ("MOTOR", [
                ("Nivel de aceite", True),
                ("Nivel de refrigerante", True),
                ("Nivel de combustible", False),
                ("Fugas visibles", True),
                ("Filtro de aire", False),
            ]),
            ("SISTEMA HIDRÁULICO", [
                ("Nivel de aceite hidráulico", True),
                ("Fugas de aceite hidráulico", True),
                ("Cilindros de levante", False),
                ("Cilindros de volteo", False),
                ("Mangueras", False),
                ("Acople rápido", False),
            ]),
            ("SISTEMA ELÉCTRICO", [
                ("Batería", False),
                ("Luces de trabajo", True),
                ("Luces de emergencia", True),
                ("Bocina", False),
                ("Panel de instrumentos", False),
            ]),
            ("SEGURIDAD", [
                ("Cinturón de seguridad", True),
                ("Barra de seguridad", True),
                ("Alarma de retroceso", True),
                ("Extintor", True),
                ("Estructura ROPS", True),
            ]),
            ("TREN DE RODAJE", [
                ("Orugas o neumáticos", True),
                ("Tensión de cadenas (si aplica)", False),
                ("Freno de estacionamiento", True),
            ]),
            ("IMPLEMENTOS", [
                ("Cuchara", False),
                ("Acople rápido", True),
                ("Pasadores", True),
                ("Dientes (si aplica)", False),
            ]),
        ]
    )
    
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    total = ChecklistTemplate.objects.count()
    print(f"✅ Total de templates en la base de datos: {total}")
    
    # Mostrar equipos por tipo
    print("\n📊 EQUIPOS POR TIPO:")
    for template in ChecklistTemplate.objects.all():
        equipos_count = template.tipo_equipo.equipos_set.filter(activo=True).count()
        print(f"   {template.tipo_equipo.nombretipo}: {equipos_count} equipos activos")

if __name__ == '__main__':
    main()
