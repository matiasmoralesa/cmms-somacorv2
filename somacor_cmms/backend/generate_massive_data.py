#!/usr/bin/env python
"""
Script para generar 2000+ registros distribuidos en todo el sistema CMMS
"""
import os
import django
import sys
import random
from datetime import datetime, timedelta
from django.utils import timezone
from faker import Faker

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import *
from django.contrib.auth.models import User

# Configurar Faker en español
fake = Faker('es_ES')

def create_massive_data():
    print("🚀 Generando 2000+ registros para el sistema CMMS...")
    
    # Contadores para tracking
    created_counts = {
        'faenas': 0,
        'tipos_equipo': 0,
        'equipos': 0,
        'usuarios': 0,
        'ordenes_trabajo': 0,
        'checklist_templates': 0,
        'checklist_instances': 0,
        'planes_mantenimiento': 0,
        'tareas_estandar': 0
    }
    
    # 1. CREAR FAENAS (15 faenas)
    print("📍 Creando faenas...")
    faenas_data = [
        'Faena Norte', 'Faena Sur', 'Faena Central', 'Faena Este', 'Faena Oeste',
        'Mina El Cobre', 'Mina La Esperanza', 'Mina San José', 'Cantera Norte',
        'Cantera Sur', 'Planta Procesamiento', 'Puerto Marítimo', 'Base Logística',
        'Campamento Principal', 'Taller Central'
    ]
    
    faenas = []
    for i, nombre in enumerate(faenas_data, 1):
        try:
            faena, created = Faenas.objects.get_or_create(
                nombrefaena=nombre,  # Buscar por nombre
                defaults={
                    'ubicacion': fake.city(),
                    'direccion': fake.address(),
                    'ciudad': fake.city(),
                    'region': fake.state(),
                    'contacto': fake.name(),
                    'telefono': fake.phone_number(),
                    'email': fake.email(),
                    'descripcion': fake.text(max_nb_chars=200),
                    'activa': random.choice([True, True, True, False])  # 75% activas
                }
            )
            if created:
                created_counts['faenas'] += 1
            faenas.append(faena)
        except:
            # Si hay conflicto, obtener el existente
            faena = Faenas.objects.filter(nombrefaena=nombre).first()
            if faena:
                faenas.append(faena)
    
    # 2. CREAR TIPOS DE EQUIPO (25 tipos)
    print("🔧 Creando tipos de equipo...")
    tipos_equipo_data = [
        'Minicargador', 'Excavadora', 'Retroexcavadora', 'Cargador Frontal', 'Bulldozer',
        'Grúa Móvil', 'Camión Tolva', 'Camión Cisterna', 'Motoniveladora', 'Compactador',
        'Perforadora', 'Volquete', 'Camioneta', 'Camión Pluma', 'Tractor',
        'Generador', 'Compresor', 'Bomba de Agua', 'Soldadora', 'Martillo Neumático',
        'Montacargas', 'Plataforma Elevadora', 'Rodillo Compactador', 'Fresadora', 'Pavimentadora'
    ]
    
    tipos_equipo = []
    for i, nombre in enumerate(tipos_equipo_data, 1):
        try:
            tipo, created = TiposEquipo.objects.get_or_create(
                nombretipo=nombre,  # Buscar por nombre en lugar de ID
                defaults={'idtipoequipo': i}
            )
            if created:
                created_counts['tipos_equipo'] += 1
            tipos_equipo.append(tipo)
        except:
            # Si hay conflicto, obtener el existente
            tipo = TiposEquipo.objects.filter(nombretipo=nombre).first()
            if tipo:
                tipos_equipo.append(tipo)
    
    # 3. CREAR ESTADOS DE EQUIPO
    estados_equipo = []
    estados_data = ['Operativo', 'En Mantenimiento', 'Fuera de Servicio', 'En Reparación', 'Disponible']
    for i, nombre in enumerate(estados_data, 1):
        estado, _ = EstadosEquipo.objects.get_or_create(
            idestadoequipo=i,
            defaults={'nombreestado': nombre}
        )
        estados_equipo.append(estado)
    
    # 4. CREAR EQUIPOS (300 equipos)
    print("🚜 Creando equipos...")
    marcas = ['Caterpillar', 'Komatsu', 'Volvo', 'JCB', 'Case', 'Liebherr', 'Hitachi', 'Doosan', 'Hyundai', 'Bobcat']
    
    for i in range(1, 301):
        tipo_equipo = random.choice(tipos_equipo)
        marca = random.choice(marcas)
        
        equipo, created = Equipos.objects.get_or_create(
            idequipo=i,
            defaults={
                'nombreequipo': f"{tipo_equipo.nombretipo} {marca}-{i:03d}",
                'codigointerno': f"{marca[:3].upper()}-{i:03d}",
                'marca': marca,
                'modelo': f"{random.choice(['200', '300', '400', '500'])}{random.choice(['D', 'L', 'X', 'H'])}",
                'anio': random.randint(2015, 2024),
                'patente': f"{fake.license_plate()[:6]}",
                'idtipoequipo': tipo_equipo,
                'idestadoactual': random.choice(estados_equipo),
                'idfaenaactual': random.choice(faenas),
                'activo': random.choice([True, True, True, False])  # 75% activos
            }
        )
        if created:
            created_counts['equipos'] += 1
    
    # 5. CREAR ROLES Y USUARIOS (50 usuarios)
    print("👥 Creando usuarios...")
    
    # Crear roles
    roles_data = [
        'Administrador', 'Supervisor', 'Técnico Senior', 'Técnico Junior', 
        'Operador', 'Jefe de Turno', 'Planificador'
    ]
    
    roles = []
    for i, nombre in enumerate(roles_data, 1):
        rol, _ = Roles.objects.get_or_create(
            nombrerol=nombre,
            defaults={'idrol': i}
        )
        roles.append(rol)
    
    # Crear usuarios Django y perfiles CMMS
    cargos = ['Técnico Mecánico', 'Técnico Eléctrico', 'Operador de Equipo', 'Supervisor de Turno', 
              'Jefe de Mantenimiento', 'Planificador de Mantenimiento', 'Soldador', 'Lubricador']
    
    for i in range(1, 51):
        # Usuario Django
        username = f"usuario{i:02d}"
        django_user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'email': fake.email(),
                'is_active': True
            }
        )
        
        if created:
            django_user.set_password('password123')
            django_user.save()
        
        # Perfil CMMS
        usuario_cmms, created = Usuarios.objects.get_or_create(
            user=django_user,
            defaults={
                'idrol': random.choice(roles),
                'departamento': random.choice(['Mantenimiento', 'Operaciones', 'Administración'])
            }
        )
        if created:
            created_counts['usuarios'] += 1
    
    # 6. CREAR TIPOS Y ESTADOS PARA ÓRDENES DE TRABAJO
    tipos_mantenimiento = []
    tipos_data = ['Preventivo', 'Correctivo', 'Predictivo', 'Emergencia', 'Modificativo']
    for i, nombre in enumerate(tipos_data, 1):
        tipo, _ = TiposMantenimientoOT.objects.get_or_create(
            idtipomantenimientoot=i,
            defaults={'nombretipomantenimientoot': nombre}
        )
        tipos_mantenimiento.append(tipo)
    
    estados_ot = []
    estados_data = ['Abierta', 'Asignada', 'En Progreso', 'Completada', 'Cancelada', 'Pendiente Aprobación']
    for i, nombre in enumerate(estados_data, 1):
        estado, _ = EstadosOrdenTrabajo.objects.get_or_create(
            idestadoot=i,
            defaults={'nombreestadoot': nombre}
        )
        estados_ot.append(estado)
    
    # 7. CREAR ÓRDENES DE TRABAJO (800 órdenes)
    print("📋 Creando órdenes de trabajo...")
    
    equipos_list = list(Equipos.objects.all())
    usuarios_django = list(User.objects.all())
    prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
    
    descripciones_preventivo = [
        'Cambio de aceite y filtros', 'Revisión de frenos', 'Mantenimiento 500 horas',
        'Inspección general', 'Cambio de correas', 'Revisión sistema hidráulico',
        'Mantenimiento sistema eléctrico', 'Cambio de neumáticos', 'Lubricación general'
    ]
    
    descripciones_correctivo = [
        'Falla en motor', 'Problema sistema hidráulico', 'Avería sistema eléctrico',
        'Fuga de aceite', 'Ruido extraño en transmisión', 'Sobrecalentamiento',
        'Pérdida de potencia', 'Vibración excesiva', 'Falla en frenos'
    ]
    
    for i in range(1, 801):
        tipo_mantenimiento = random.choice(tipos_mantenimiento)
        
        if tipo_mantenimiento.nombretipomantenimientoot == 'Preventivo':
            descripcion = random.choice(descripciones_preventivo)
        else:
            descripcion = random.choice(descripciones_correctivo)
        
        # Fechas realistas
        fecha_creacion = fake.date_time_between(start_date='-6M', end_date='now', tzinfo=timezone.get_current_timezone())
        
        # Estado basado en la antigüedad
        dias_desde_creacion = (timezone.now() - fecha_creacion).days
        if dias_desde_creacion > 30:
            estado = random.choice([estados_ot[3], estados_ot[4]])  # Completada o Cancelada
        elif dias_desde_creacion > 7:
            estado = random.choice([estados_ot[2], estados_ot[3]])  # En Progreso o Completada
        else:
            estado = random.choice([estados_ot[0], estados_ot[1], estados_ot[2]])  # Abierta, Asignada, En Progreso
        
        fecha_completado = None
        if estado.nombreestadoot == 'Completada':
            fecha_completado = fecha_creacion + timedelta(days=random.randint(1, 15))
        
        orden, created = OrdenesTrabajo.objects.get_or_create(
            numeroot=f"OT-{i:04d}",
            defaults={
                'idequipo': random.choice(equipos_list),
                'idtipomantenimientoot': tipo_mantenimiento,
                'idestadoot': estado,
                'idsolicitante': random.choice(usuarios_django),
                'idtecnicoasignado': random.choice(usuarios_django) if random.random() > 0.2 else None,
                'descripcionproblemareportado': descripcion,
                'prioridad': random.choice(prioridades),
                'fechacreacionot': fecha_creacion,
                'fechacompletado': fecha_completado,
                'tiempototalminutos': random.randint(30, 480) if fecha_completado else None,
                'horometro': random.randint(100, 5000),
                'observacionesfinales': fake.text(max_nb_chars=200) if fecha_completado else None
            }
        )
        if created:
            created_counts['ordenes_trabajo'] += 1
    
    # 8. CREAR TIPOS DE TAREA Y TAREAS ESTÁNDAR (100 tareas)
    print("⚙️ Creando tareas estándar...")
    
    tipos_tarea_data = [
        'Inspección', 'Lubricación', 'Reemplazo', 'Ajuste', 'Limpieza',
        'Calibración', 'Reparación', 'Soldadura', 'Pintura', 'Prueba'
    ]
    
    tipos_tarea = []
    for i, nombre in enumerate(tipos_tarea_data, 1):
        tipo, _ = TiposTarea.objects.get_or_create(
            idtipotarea=i,
            defaults={'nombretipotarea': nombre, 'descripcion': f'Tareas de {nombre.lower()}'}
        )
        tipos_tarea.append(tipo)
    
    tareas_por_tipo = {
        'Inspección': ['Inspección visual', 'Verificación de niveles', 'Control de presiones', 'Revisión de conexiones'],
        'Lubricación': ['Engrase de puntos', 'Cambio de aceite motor', 'Cambio aceite hidráulico', 'Lubricación cadenas'],
        'Reemplazo': ['Cambio de filtros', 'Reemplazo de correas', 'Cambio de bujías', 'Reemplazo de mangueras'],
        'Ajuste': ['Ajuste de frenos', 'Calibración de válvulas', 'Tensado de correas', 'Ajuste de cadenas'],
        'Limpieza': ['Limpieza de radiador', 'Limpieza de filtros', 'Lavado exterior', 'Limpieza cabina']
    }
    
    for i in range(1, 101):
        tipo_tarea = random.choice(tipos_tarea)
        tareas_disponibles = tareas_por_tipo.get(tipo_tarea.nombretipotarea, ['Tarea general'])
        
        tarea, created = TareasEstandar.objects.get_or_create(
            idtareaestandar=i,
            defaults={
                'nombretarea': random.choice(tareas_disponibles) + f" #{i}",
                'descripciontarea': fake.text(max_nb_chars=150),
                'idtipotarea': tipo_tarea,
                'tiempoestimadominutos': random.randint(15, 240),
                'activa': random.choice([True, True, True, False])
            }
        )
        if created:
            created_counts['tareas_estandar'] += 1
    
    # 9. CREAR PLANES DE MANTENIMIENTO (50 planes)
    print("📅 Creando planes de mantenimiento...")
    
    for i in range(1, 51):
        tipo_equipo = random.choice(tipos_equipo)
        
        plan, created = PlanesMantenimiento.objects.get_or_create(
            idplanmantenimiento=i,
            defaults={
                'nombreplan': f"Plan {tipo_equipo.nombretipo} - Tipo {i}",
                'descripcionplan': f"Plan de mantenimiento preventivo para {tipo_equipo.nombretipo}",
                'idtipoequipo': tipo_equipo,
                'activo': True
            }
        )
        if created:
            created_counts['planes_mantenimiento'] += 1
    
    # 10. CREAR CHECKLIST TEMPLATES (30 templates)
    print("✅ Creando templates de checklist...")
    
    for i in range(1, 31):
        tipo_equipo = random.choice(tipos_equipo)
        
        template, created = ChecklistTemplate.objects.get_or_create(
            id_template=i,
            defaults={
                'nombre': f"Checklist {tipo_equipo.nombretipo}",
                'tipo_equipo': tipo_equipo,
                'activo': True
            }
        )
        if created:
            created_counts['checklist_templates'] += 1
            
            # Crear categorías para cada template
            categorias = ['MOTOR', 'SISTEMA HIDRÁULICO', 'FRENOS', 'LUCES', 'DOCUMENTOS']
            for j, cat_nombre in enumerate(categorias, 1):
                categoria, _ = ChecklistCategory.objects.get_or_create(
                    template=template,
                    nombre=cat_nombre,
                    defaults={'orden': j}
                )
                
                # Crear items para cada categoría
                items_por_categoria = {
                    'MOTOR': ['Nivel de aceite', 'Temperatura', 'Ruidos extraños', 'Fugas'],
                    'SISTEMA HIDRÁULICO': ['Presión', 'Nivel de fluido', 'Mangueras', 'Cilindros'],
                    'FRENOS': ['Funcionamiento', 'Nivel de fluido', 'Pastillas', 'Discos'],
                    'LUCES': ['Faros delanteros', 'Luces traseras', 'Intermitentes', 'Luz de trabajo'],
                    'DOCUMENTOS': ['Licencia operador', 'Certificado técnico', 'Seguro vigente', 'Revisión técnica']
                }
                
                items = items_por_categoria.get(cat_nombre, ['Item general'])
                for k, item_texto in enumerate(items, 1):
                    ChecklistItem.objects.get_or_create(
                        category=categoria,
                        texto=item_texto,
                        defaults={
                            'orden': k,
                            'es_critico': random.choice([True, False])
                        }
                    )
    
    # 11. CREAR CHECKLIST INSTANCES (400 instancias)
    print("📝 Creando instancias de checklist...")
    
    templates_list = list(ChecklistTemplate.objects.all())
    
    for i in range(1, 401):
        template = random.choice(templates_list)
        equipo = random.choice([e for e in equipos_list if e.idtipoequipo == template.tipo_equipo])
        
        fecha_inspeccion = fake.date_between(start_date='-3M', end_date='today')
        
        instance, created = ChecklistInstance.objects.get_or_create(
            id_instance=i,
            defaults={
                'template': template,
                'equipo': equipo,
                'operador': random.choice(usuarios_django),
                'fecha_inspeccion': fecha_inspeccion,
                'horometro_inspeccion': random.randint(100, 5000),
                'lugar_inspeccion': random.choice(faenas).nombrefaena,
                'observaciones_generales': fake.text(max_nb_chars=200) if random.random() > 0.5 else None
            }
        )
        if created:
            created_counts['checklist_instances'] += 1
            
            # Crear respuestas para cada item del template
            for categoria in template.categories.all():
                for item in categoria.items.all():
                    ChecklistAnswer.objects.get_or_create(
                        instance=instance,
                        item=item,
                        defaults={
                            'estado': random.choice(['bueno', 'malo', 'na']),
                            'observacion_item': fake.sentence() if random.random() > 0.7 else None
                        }
                    )
    
    # RESUMEN FINAL
    total_created = sum(created_counts.values())
    
    print(f"\n🎉 GENERACIÓN MASIVA COMPLETADA!")
    print(f"📊 RESUMEN DE REGISTROS CREADOS:")
    print(f"   📍 Faenas: {created_counts['faenas']}")
    print(f"   🔧 Tipos de Equipo: {created_counts['tipos_equipo']}")
    print(f"   🚜 Equipos: {created_counts['equipos']}")
    print(f"   👥 Usuarios: {created_counts['usuarios']}")
    print(f"   📋 Órdenes de Trabajo: {created_counts['ordenes_trabajo']}")
    print(f"   ⚙️ Tareas Estándar: {created_counts['tareas_estandar']}")
    print(f"   📅 Planes de Mantenimiento: {created_counts['planes_mantenimiento']}")
    print(f"   ✅ Templates de Checklist: {created_counts['checklist_templates']}")
    print(f"   📝 Instancias de Checklist: {created_counts['checklist_instances']}")
    print(f"\n🎯 TOTAL DE REGISTROS NUEVOS: {total_created}")
    
    # Estadísticas finales del sistema
    print(f"\n📈 ESTADÍSTICAS FINALES DEL SISTEMA:")
    print(f"   📍 Faenas: {Faenas.objects.count()}")
    print(f"   🔧 Tipos de Equipo: {TiposEquipo.objects.count()}")
    print(f"   🚜 Equipos: {Equipos.objects.count()}")
    print(f"   👥 Usuarios Django: {User.objects.count()}")
    print(f"   👤 Perfiles CMMS: {Usuarios.objects.count()}")
    print(f"   📋 Órdenes de Trabajo: {OrdenesTrabajo.objects.count()}")
    print(f"   ⚙️ Tareas Estándar: {TareasEstandar.objects.count()}")
    print(f"   📅 Planes de Mantenimiento: {PlanesMantenimiento.objects.count()}")
    print(f"   ✅ Templates de Checklist: {ChecklistTemplate.objects.count()}")
    print(f"   📝 Instancias de Checklist: {ChecklistInstance.objects.count()}")
    print(f"   💬 Respuestas de Checklist: {ChecklistAnswer.objects.count()}")
    
    total_records = (Faenas.objects.count() + TiposEquipo.objects.count() + 
                    Equipos.objects.count() + User.objects.count() + 
                    OrdenesTrabajo.objects.count() + TareasEstandar.objects.count() +
                    ChecklistInstance.objects.count() + ChecklistAnswer.objects.count())
    
    print(f"\n🎊 TOTAL DE REGISTROS EN EL SISTEMA: {total_records}")

if __name__ == '__main__':
    create_massive_data()