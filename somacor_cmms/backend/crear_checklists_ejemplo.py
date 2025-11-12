"""
Script para crear templates de checklist de ejemplo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import ChecklistTemplate, ChecklistCategory, ChecklistItem, TiposEquipo

def crear_checklists():
    print("Creando templates de checklist...")
    
    # Obtener tipos de equipo
    tipos_equipo = TiposEquipo.objects.all()
    
    if not tipos_equipo.exists():
        print("❌ No hay tipos de equipo en la base de datos")
        return
    
    # Crear template para cada tipo de equipo
    for tipo in tipos_equipo[:3]:  # Primeros 3 tipos
        # Verificar si ya existe un template para este tipo
        if ChecklistTemplate.objects.filter(tipo_equipo=tipo).exists():
            print(f"⏭️  Ya existe template para {tipo.nombretipo}")
            continue
            
        template = ChecklistTemplate.objects.create(
            nombre=f"Checklist Diario - {tipo.nombretipo}",
            tipo_equipo=tipo,
            activo=True
        )
        print(f"✅ Template creado: {template.nombre}")
        
        # Categoría 1: Motor
        cat_motor = ChecklistCategory.objects.create(
            template=template,
            nombre="Motor y Sistema de Combustible",
            orden=1
        )
        
        items_motor = [
            ("Nivel de aceite del motor", True),
            ("Fugas de aceite", True),
            ("Nivel de refrigerante", True),
            ("Fugas de refrigerante", True),
            ("Nivel de combustible", False),
            ("Fugas de combustible", True),
            ("Filtro de aire", False),
            ("Correas y mangueras", False),
        ]
        
        for orden, (texto, critico) in enumerate(items_motor, 1):
            ChecklistItem.objects.create(
                category=cat_motor,
                texto=texto,
                es_critico=critico,
                orden=orden
            )
        
        # Categoría 2: Sistema Hidráulico
        cat_hidraulico = ChecklistCategory.objects.create(
            template=template,
            nombre="Sistema Hidráulico",
            orden=2
        )
        
        items_hidraulico = [
            ("Nivel de aceite hidráulico", True),
            ("Fugas de aceite hidráulico", True),
            ("Mangueras hidráulicas", False),
            ("Cilindros hidráulicos", False),
            ("Presión del sistema", True),
        ]
        
        for orden, (texto, critico) in enumerate(items_hidraulico, 1):
            ChecklistItem.objects.create(
                category=cat_hidraulico,
                texto=texto,
                es_critico=critico,
                orden=orden
            )
        
        # Categoría 3: Sistema Eléctrico
        cat_electrico = ChecklistCategory.objects.create(
            template=template,
            nombre="Sistema Eléctrico",
            orden=3
        )
        
        items_electrico = [
            ("Batería y terminales", False),
            ("Luces delanteras", True),
            ("Luces traseras", True),
            ("Luces de emergencia", True),
            ("Bocina", False),
            ("Instrumentos del tablero", False),
        ]
        
        for orden, (texto, critico) in enumerate(items_electrico, 1):
            ChecklistItem.objects.create(
                category=cat_electrico,
                texto=texto,
                es_critico=critico,
                orden=orden
            )
        
        # Categoría 4: Seguridad
        cat_seguridad = ChecklistCategory.objects.create(
            template=template,
            nombre="Elementos de Seguridad",
            orden=4
        )
        
        items_seguridad = [
            ("Cinturón de seguridad", True),
            ("Espejos retrovisores", True),
            ("Extintor", True),
            ("Botiquín de primeros auxilios", False),
            ("Señalización de seguridad", False),
            ("Alarma de retroceso", True),
        ]
        
        for orden, (texto, critico) in enumerate(items_seguridad, 1):
            ChecklistItem.objects.create(
                category=cat_seguridad,
                texto=texto,
                es_critico=critico,
                orden=orden
            )
        
        # Categoría 5: Neumáticos y Frenos
        cat_neumaticos = ChecklistCategory.objects.create(
            template=template,
            nombre="Neumáticos y Sistema de Frenos",
            orden=5
        )
        
        items_neumaticos = [
            ("Presión de neumáticos", True),
            ("Estado de neumáticos", True),
            ("Freno de servicio", True),
            ("Freno de estacionamiento", True),
            ("Nivel de líquido de frenos", True),
        ]
        
        for orden, (texto, critico) in enumerate(items_neumaticos, 1):
            ChecklistItem.objects.create(
                category=cat_neumaticos,
                texto=texto,
                es_critico=critico,
                orden=orden
            )
        
        print(f"   📋 5 categorías creadas con {len(items_motor) + len(items_hidraulico) + len(items_electrico) + len(items_seguridad) + len(items_neumaticos)} items")
    
    total_templates = ChecklistTemplate.objects.count()
    print(f"\n✅ Total de templates en la base de datos: {total_templates}")

if __name__ == '__main__':
    crear_checklists()
