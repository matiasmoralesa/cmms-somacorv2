#!/usr/bin/env python3
"""
Script para poblar las plantillas de checklist según los documentos proporcionados
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/home/ubuntu/cmms-somacorv2/somacor_cmms/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import TiposEquipo, ChecklistTemplate, ChecklistCategory, ChecklistItem

def crear_checklist_cargador_frontal():
    """Crear checklist para Cargador Frontal según F-PR-037-CH01"""
    print("Creando checklist para Cargador Frontal...")
    
    tipo_equipo = TiposEquipo.objects.get(nombretipo="Cargador Frontal")
    
    # Crear plantilla
    template, created = ChecklistTemplate.objects.get_or_create(
        nombre="Check List Cargador Frontal (Diario)",
        tipo_equipo=tipo_equipo,
        defaults={'activo': True}
    )
    
    if not created:
        print(f"  - Plantilla ya existe, limpiando items anteriores...")
        ChecklistItem.objects.filter(category__template=template).delete()
        ChecklistCategory.objects.filter(template=template).delete()
    
    # Categoría 1: MOTOR
    cat_motor = ChecklistCategory.objects.create(
        template=template,
        nombre="MOTOR",
        orden=1
    )
    items_motor = [
        "Nivel de Agua", "Nivel de Aceite", "Nivel de Líquido de Freno",
        "Batería", "Correas", "Filtraciones", "Alternador", "Partida en Frío",
        "Radiador / Anticongelante", "Motor Arranque"
    ]
    for idx, item in enumerate(items_motor, 1):
        ChecklistItem.objects.create(
            category=cat_motor,
            texto=item,
            orden=idx,
            es_critico=(item in ["Batería", "Correas"])
        )
    
    # Categoría 2: LUCES
    cat_luces = ChecklistCategory.objects.create(
        template=template,
        nombre="LUCES",
        orden=2
    )
    items_luces = [
        "Luces Altas", "Luces Bajas", "Luces Intermitentes", "Luz Marcha Atrás",
        "Luz Interior", "Luz Patente", "Luz Tablero", "Luz Baliza", "Luz Pértiga",
        "Luces de Freno", "Estado de Micas"
    ]
    for idx, item in enumerate(items_luces, 1):
        ChecklistItem.objects.create(
            category=cat_luces,
            texto=item,
            orden=idx,
            es_critico=(item in ["Luces Altas", "Luces Bajas"])
        )
    
    # Categoría 3: DOCUMENTOS
    cat_docs = ChecklistCategory.objects.create(
        template=template,
        nombre="DOCUMENTOS",
        orden=3
    )
    items_docs = ["Permiso de Circulación", "Revisión Técnica", "Seguro Obligatorio"]
    for idx, item in enumerate(items_docs, 1):
        ChecklistItem.objects.create(
            category=cat_docs,
            texto=item,
            orden=idx,
            es_critico=True
        )
    
    # Categoría 4: ACCESORIOS
    cat_accesorios = ChecklistCategory.objects.create(
        template=template,
        nombre="ACCESORIOS",
        orden=4
    )
    items_accesorios = [
        "Cinturón de Seguridad", "Extintor (8-10 kilos) (A-B-C)/ Sistema AFEX",
        "Marcadores", "Triángulos / Conos", "Chapas de Puertas", "Calefacción",
        "Limpia parabrisas", "Vidrios", "Manillas de Puertas", "Asiento",
        "Espejo Retrovisor", "Espejos Laterales", "Estado de Carrocería en General",
        "Bocina / Alarma de Retroceso", "Aire Acondicionado", "Cuñas",
        "Estado de neumáticos", "Seguros en tuercas", "Dirección (Mecánica o Hidráulica)",
        "Tubo de Escape", "Estado pasamanos", "Escaleras de acceso",
        "Se ha sobrecargado el sistema eléctrico original del equipo?"
    ]
    for idx, item in enumerate(items_accesorios, 1):
        ChecklistItem.objects.create(
            category=cat_accesorios,
            texto=item,
            orden=idx,
            es_critico=(item in ["Cinturón de Seguridad", "Estado de neumáticos", "Dirección (Mecánica o Hidráulica)"])
        )
    
    # Categoría 5: FRENOS
    cat_frenos = ChecklistCategory.objects.create(
        template=template,
        nombre="FRENOS",
        orden=5
    )
    items_frenos = ["Freno de Servicio", "Freno de Parqueo"]
    for idx, item in enumerate(items_frenos, 1):
        ChecklistItem.objects.create(
            category=cat_frenos,
            texto=item,
            orden=idx,
            es_critico=True
        )
    
    # Categoría 6: CARGADOR FRONTAL (Específico)
    cat_cargador = ChecklistCategory.objects.create(
        template=template,
        nombre="CARGADOR FRONTAL",
        orden=6
    )
    items_cargador = [
        "Grietas", "Indicador de Ángulo", "Calzas", "Seguros", "Balde",
        "Sistema hidráulico", "Mangueras hidráulicas", "Conexiones hidráulicas",
        "Sistema Corta Corriente", "Desgaste dientes", "Mandos Operacional",
        "Sistema de Levante", "Sistema Engrase"
    ]
    for idx, item in enumerate(items_cargador, 1):
        ChecklistItem.objects.create(
            category=cat_cargador,
            texto=item,
            orden=idx,
            es_critico=(item in ["Sistema Corta Corriente", "Mandos Operacional"])
        )
    
    print(f"  ✅ Checklist Cargador Frontal creado con {ChecklistItem.objects.filter(category__template=template).count()} items")

def crear_checklist_retroexcavadora():
    """Crear checklist para Retroexcavadora según F-PR-034-CH01"""
    print("Creando checklist para Retroexcavadora...")
    
    tipo_equipo = TiposEquipo.objects.get(nombretipo="Retroexcavadora")
    
    # Crear plantilla
    template, created = ChecklistTemplate.objects.get_or_create(
        nombre="Inspección Retroexcavadora (Diario)",
        tipo_equipo=tipo_equipo,
        defaults={'activo': True}
    )
    
    if not created:
        print(f"  - Plantilla ya existe, limpiando items anteriores...")
        ChecklistItem.objects.filter(category__template=template).delete()
        ChecklistCategory.objects.filter(template=template).delete()
    
    # Categoría 1: MOTOR
    cat_motor = ChecklistCategory.objects.create(
        template=template,
        nombre="MOTOR",
        orden=1
    )
    items_motor = [
        "Nivel de Agua", "Nivel de Aceite", "Nivel de Hidráulico", "Batería",
        "Correas", "Filtraciones (Aceite / Combustible)", "Alternador",
        "Partida en Frío", "Radiador / Anticongelante", "Motor Arranque"
    ]
    for idx, item in enumerate(items_motor, 1):
        ChecklistItem.objects.create(
            category=cat_motor,
            texto=item,
            orden=idx,
            es_critico=(item in ["Filtraciones (Aceite / Combustible)"])
        )
    
    # Categoría 2: LUCES
    cat_luces = ChecklistCategory.objects.create(
        template=template,
        nombre="LUCES",
        orden=2
    )
    items_luces = [
        "Focos faeneros", "Luces Bajas", "Luces Intermitentes", "Luz Marcha Atrás",
        "Luz Interior", "Luz Patente", "Luz Tablero", "Luz Baliza", "Luz Pértiga",
        "Luces de Freno", "Estado de Micas"
    ]
    for idx, item in enumerate(items_luces, 1):
        ChecklistItem.objects.create(
            category=cat_luces,
            texto=item,
            orden=idx,
            es_critico=(item in ["Luces Bajas"])
        )
    
    # Categoría 3: DOCUMENTOS VIGENTES
    cat_docs = ChecklistCategory.objects.create(
        template=template,
        nombre="DOCUMENTOS VIGENTES",
        orden=3
    )
    items_docs = [
        "Permiso de Circulación (si aplicase)",
        "Revisión Técnica (si aplicase)",
        "Seguro Obligatorio (si aplicase)"
    ]
    for idx, item in enumerate(items_docs, 1):
        ChecklistItem.objects.create(
            category=cat_docs,
            texto=item,
            orden=idx,
            es_critico=False
        )
    
    # Categoría 4: ACCESORIOS
    cat_accesorios = ChecklistCategory.objects.create(
        template=template,
        nombre="ACCESORIOS",
        orden=4
    )
    items_accesorios = [
        "Extintor (8-10 kilos) (A-B-C)/Sistema AFEX", "Llave de Rueda", "Conos",
        "Cinturón de Seguridad", "Otros", "Chapas de Puertas", "Calefacción",
        "Limpia parabrisas", "Vidrios", "Manillas de Puertas", "Asiento",
        "Espejo Retrovisor", "Espejos Laterales", "Estado de Carrocería en General",
        "Bocina / Alarma de Retroceso", "Aire Acondicionado", "Cuñas",
        "Estado de neumáticos", "Seguros en tuercas", "Dirección (Mecánica o Hidráulica)",
        "Tubo de Escape"
    ]
    for idx, item in enumerate(items_accesorios, 1):
        ChecklistItem.objects.create(
            category=cat_accesorios,
            texto=item,
            orden=idx,
            es_critico=(item in ["Estado de neumáticos", "Dirección (Mecánica o Hidráulica)"])
        )
    
    # Categoría 5: FRENOS
    cat_frenos = ChecklistCategory.objects.create(
        template=template,
        nombre="FRENOS",
        orden=5
    )
    items_frenos = ["Freno de Servicio", "Freno Parqueo"]
    for idx, item in enumerate(items_frenos, 1):
        ChecklistItem.objects.create(
            category=cat_frenos,
            texto=item,
            orden=idx,
            es_critico=True
        )
    
    # Categoría 6: ELEMENTOS RETROEXCAVADORA (Específico)
    cat_retro = ChecklistCategory.objects.create(
        template=template,
        nombre="ELEMENTOS RETROEXCAVADORA",
        orden=6
    )
    items_retro = [
        "Juego Pasador Balde", "Juego Bujes", "Desgaste Cuchillos", "Desgaste Dientes",
        "Desgaste Cadena", "Sistema Hidráulico", "Mangueras Hidráulicas",
        "Conexiones Hidráulicas", "Sistema corta corriente", "Estado de Aguilón",
        "Martillo Hidráulico", "Mandos Operacionales", "Otros"
    ]
    for idx, item in enumerate(items_retro, 1):
        ChecklistItem.objects.create(
            category=cat_retro,
            texto=item,
            orden=idx,
            es_critico=(item in ["Sistema corta corriente"])
        )
    
    print(f"  ✅ Checklist Retroexcavadora creado con {ChecklistItem.objects.filter(category__template=template).count()} items")

def crear_checklist_camioneta():
    """Crear checklist para Camionetas según F-PR-020-CH01"""
    print("Creando checklist para Camionetas...")
    
    tipo_equipo = TiposEquipo.objects.get(nombretipo="Camioneta")
    
    # Crear plantilla
    template, created = ChecklistTemplate.objects.get_or_create(
        nombre="Check List Camionetas (Diario)",
        tipo_equipo=tipo_equipo,
        defaults={'activo': True}
    )
    
    if not created:
        print(f"  - Plantilla ya existe, limpiando items anteriores...")
        ChecklistItem.objects.filter(category__template=template).delete()
        ChecklistCategory.objects.filter(template=template).delete()
    
    # Categoría 1: AUTO EVALUACIÓN DEL OPERADOR
    cat_auto = ChecklistCategory.objects.create(
        template=template,
        nombre="AUTO EVALUACIÓN DEL OPERADOR",
        orden=1
    )
    items_auto = [
        "Cumplo con descanso suficiente y condiciones para manejo seguro",
        "Cumplo con condiciones físicas adecuadas y no tengo dolencias o enfermedades que me impidan conducir",
        "Estoy conciente de mi responsabilidad al conducir, sin poner en riesgo mi integridad ni la de mis compañeros o de patrimonio de la empresa"
    ]
    for idx, item in enumerate(items_auto, 1):
        ChecklistItem.objects.create(
            category=cat_auto,
            texto=item,
            orden=idx,
            es_critico=True
        )
    
    # Categoría 2: DOCUMENTACIÓN DEL OPERADOR
    cat_docs_op = ChecklistCategory.objects.create(
        template=template,
        nombre="DOCUMENTACIÓN DEL OPERADOR",
        orden=2
    )
    items_docs_op = ["Licencia Municipal", "Licencia interna de Faena"]
    for idx, item in enumerate(items_docs_op, 1):
        ChecklistItem.objects.create(
            category=cat_docs_op,
            texto=item,
            orden=idx,
            es_critico=True
        )
    
    # Categoría 3: REQUISITOS
    cat_requisitos = ChecklistCategory.objects.create(
        template=template,
        nombre="REQUISITOS",
        orden=3
    )
    items_requisitos = [
        "Aire acondicionado/ calefacción",
        "Baliza y pértiga (funcionando y en condiciones)",
        "Bocina en buen estado",
        "Cinturones de Seguridad en buen estado",
        "Cuñas de seguridad disponibles (2)",
        "Espejos interior y exterior en condiciones y limpios",
        "Frenos (incluye freno de mano) en condiciones operativas",
        "Neumáticos en buen estado (incluye dos repuestos)",
        "Luces (Altas, Bajas, Frenos, intermitentes, retroceso)",
        "Sello caja de operación invierno en buenas condiciones"
    ]
    for idx, item in enumerate(items_requisitos, 1):
        ChecklistItem.objects.create(
            category=cat_requisitos,
            texto=item,
            orden=idx,
            es_critico=(item in ["Frenos (incluye freno de mano) en condiciones operativas", "Neumáticos en buen estado (incluye dos repuestos)"])
        )
    
    # Categoría 4: CONDICIONES PARA REQUISITOS COMPLEMENTARIOS
    cat_complementarios = ChecklistCategory.objects.create(
        template=template,
        nombre="CONDICIONES PARA REQUISITOS COMPLEMENTARIOS",
        orden=4
    )
    items_complementarios = [
        "Orden y Aseo (interior vehículo y pick up)",
        "Estado de carrocería, parachoques, portañón",
        "Gata y llave de rueda disponible",
        "Vidrios y parabrisas limpios",
        "Limpiaparabrisas funciona correctamente",
        "Radio Base funciona en todos los canales"
    ]
    for idx, item in enumerate(items_complementarios, 1):
        ChecklistItem.objects.create(
            category=cat_complementarios,
            texto=item,
            orden=idx,
            es_critico=False
        )
    
    # Categoría 5: DOCUMENTACIÓN
    cat_docs = ChecklistCategory.objects.create(
        template=template,
        nombre="DOCUMENTACIÓN",
        orden=5
    )
    items_docs = ["Permiso de Circulación", "Revisión Técnica", "Seguro Obligatorio"]
    for idx, item in enumerate(items_docs, 1):
        ChecklistItem.objects.create(
            category=cat_docs,
            texto=item,
            orden=idx,
            es_critico=True
        )
    
    print(f"  ✅ Checklist Camionetas creado con {ChecklistItem.objects.filter(category__template=template).count()} items")

def crear_checklist_camion_supersucker():
    """Crear checklist para Camión Supersucker"""
    print("Creando checklist para Camión Supersucker...")
    
    tipo_equipo = TiposEquipo.objects.get(nombretipo="Camión Supersucker")
    
    # Crear plantilla
    template, created = ChecklistTemplate.objects.get_or_create(
        nombre="Check-List Estado de Vehículo - Camión Supersucker",
        tipo_equipo=tipo_equipo,
        defaults={'activo': True}
    )
    
    if not created:
        print(f"  - Plantilla ya existe, limpiando items anteriores...")
        ChecklistItem.objects.filter(category__template=template).delete()
        ChecklistCategory.objects.filter(template=template).delete()
    
    # Categoría 1: LUCES
    cat_luces = ChecklistCategory.objects.create(
        template=template,
        nombre="LUCES",
        orden=1
    )
    items_luces = [
        "Luz baja", "Luz Alta", "Luz Marcha Atrás", "Luz Interior", "Luz de Freno",
        "Tercera Luz de Freno", "Intermitentes", "Pértiga",
        "Baliza y conexión eléctrica", "Pértiga y conexión eléctrica"
    ]
    for idx, item in enumerate(items_luces, 1):
        ChecklistItem.objects.create(
            category=cat_luces,
            texto=item,
            orden=idx,
            es_critico=False
        )
    
    # Categoría 2: DOCUMENTOS
    cat_docs = ChecklistCategory.objects.create(
        template=template,
        nombre="DOCUMENTOS",
        orden=2
    )
    items_docs = [
        "Permiso de Circulación", "Revisión Técnica", "Tarjeta de mantención",
        "Seguro Obligatorio", "Tarjeta o llave combustible", "G.P.S."
    ]
    for idx, item in enumerate(items_docs, 1):
        ChecklistItem.objects.create(
            category=cat_docs,
            texto=item,
            orden=idx,
            es_critico=True
        )
    
    # Categoría 3: ASPIRADO
    cat_aspirado = ChecklistCategory.objects.create(
        template=template,
        nombre="ASPIRADO",
        orden=3
    )
    items_aspirado = [
        "Bomba aspiradora", "Inspección ducto de succión",
        "Inspección mangueras de succión", "Sistema control descarga hidráulico"
    ]
    for idx, item in enumerate(items_aspirado, 1):
        ChecklistItem.objects.create(
            category=cat_aspirado,
            texto=item,
            orden=idx,
            es_critico=True
        )
    
    # Categoría 4: NEUMÁTICOS
    cat_neumaticos = ChecklistCategory.objects.create(
        template=template,
        nombre="NEUMÁTICOS",
        orden=4
    )
    items_neumaticos = ["Delanteros", "Traseros", "Repuestos", "Visión de Tuercas"]
    for idx, item in enumerate(items_neumaticos, 1):
        ChecklistItem.objects.create(
            category=cat_neumaticos,
            texto=item,
            orden=idx,
            es_critico=True
        )
    
    # Categoría 5: ACCESORIOS
    cat_accesorios = ChecklistCategory.objects.create(
        template=template,
        nombre="ACCESORIOS",
        orden=5
    )
    items_accesorios = [
        "Barra interna /certificado", "Extintor, Botiquín, Triángulos",
        "Cinturón de Seguridad", "Chapas de Puertas", "Bocina", "Parabrisas",
        "Vidrios laterales", "Bolso Herramientas", "Manillas Alza vidrios",
        "Batería", "Nivel de Agua", "Nivel de Aceite", "Correas de accesorios",
        "Verificar gases de escape", "Espejos Retrovisores", "Logotipo", "Cuñas",
        "Gata, y manivela", "Llave rueda", "Plumillas Limpia Vidrios"
    ]
    for idx, item in enumerate(items_accesorios, 1):
        ChecklistItem.objects.create(
            category=cat_accesorios,
            texto=item,
            orden=idx,
            es_critico=(item in ["Extintor, Botiquín, Triángulos", "Cinturón de Seguridad"])
        )
    
    # Categoría 6: ALTA MONTAÑA
    cat_montana = ChecklistCategory.objects.create(
        template=template,
        nombre="ALTA MONTAÑA",
        orden=6
    )
    items_montana = [
        "Sacos", "Cadenas para nieve", "Tensores de cadenas",
        "Pala", "Estrobos, remolque", "Linterna", "Trazadas"
    ]
    for idx, item in enumerate(items_montana, 1):
        ChecklistItem.objects.create(
            category=cat_montana,
            texto=item,
            orden=idx,
            es_critico=False
        )
    
    print(f"  ✅ Checklist Camión Supersucker creado con {ChecklistItem.objects.filter(category__template=template).count()} items")

if __name__ == "__main__":
    print("=" * 60)
    print("POBLANDO PLANTILLAS DE CHECKLIST")
    print("=" * 60)
    
    try:
        crear_checklist_cargador_frontal()
        crear_checklist_retroexcavadora()
        crear_checklist_camioneta()
        crear_checklist_camion_supersucker()
        
        print("\n" + "=" * 60)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        
        # Mostrar resumen
        total_templates = ChecklistTemplate.objects.count()
        total_categories = ChecklistCategory.objects.count()
        total_items = ChecklistItem.objects.count()
        
        print(f"\nResumen:")
        print(f"  - Plantillas creadas: {total_templates}")
        print(f"  - Categorías creadas: {total_categories}")
        print(f"  - Items creados: {total_items}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

