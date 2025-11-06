"""
Script para cargar datos de muestra V2
Datos optimizados y adaptados al nuevo formato del backend
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from django.contrib.auth.models import User
from cmms_api.models import *

def crear_usuarios():
    """Crear usuarios del sistema"""
    print("Creando usuarios...")
    
    # Crear roles
    roles_data = [
        {'nombrerol': 'Administrador'},
        {'nombrerol': 'Supervisor'},
        {'nombrerol': 'Técnico'},
        {'nombrerol': 'Operador'},
        {'nombrerol': 'Planificador'}
    ]
    
    roles = {}
    for rol_data in roles_data:
        rol, created = Roles.objects.get_or_create(
            nombrerol=rol_data['nombrerol'],
            defaults=rol_data
        )
        roles[rol_data['nombrerol']] = rol
        print(f"  Rol: {rol.nombrerol}")
    
    # Crear usuarios
    usuarios_data = [
        {'username': 'admin', 'email': 'admin@somacor.com', 'first_name': 'Administrador', 'last_name': 'Sistema', 'rol': 'Administrador'},
        {'username': 'supervisor1', 'email': 'supervisor1@somacor.com', 'first_name': 'Carlos', 'last_name': 'Mendoza', 'rol': 'Supervisor'},
        {'username': 'tecnico1', 'email': 'tecnico1@somacor.com', 'first_name': 'Juan', 'last_name': 'Pérez', 'rol': 'Técnico'},
        {'username': 'tecnico2', 'email': 'tecnico2@somacor.com', 'first_name': 'María', 'last_name': 'González', 'rol': 'Técnico'},
        {'username': 'operador1', 'email': 'operador1@somacor.com', 'first_name': 'Pedro', 'last_name': 'Rodríguez', 'rol': 'Operador'},
        {'username': 'planificador1', 'email': 'planificador1@somacor.com', 'first_name': 'Ana', 'last_name': 'López', 'rol': 'Planificador'}
    ]
    
    usuarios = {}
    for user_data in usuarios_data:
        # Crear usuario Django
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_active': True
            }
        )
        if created:
            user.set_password('password123')
            user.save()
        
        # Crear usuario CMMS
        usuario_cmms, created = Usuarios.objects.get_or_create(
            user=user,
            defaults={
                'idrol': roles[user_data['rol']],
                'departamento': 'Mantenimiento'
            }
        )
        usuarios[user_data['username']] = usuario_cmms
        print(f"  ✅ Usuario: {user.username} ({user_data['rol']})")
    
    return usuarios


def crear_tipos_equipo():
    """Crear tipos de equipo"""
    print("🔧 Creando tipos de equipo...")
    
    tipos_data = [
        {'nombretipo': 'Excavadora'},
        {'nombretipo': 'Bulldozer'},
        {'nombretipo': 'Cargador Frontal'},
        {'nombretipo': 'Camión Volquete'},
        {'nombretipo': 'Grúa'},
        {'nombretipo': 'Compactador'},
        {'nombretipo': 'Perforadora'},
        {'nombretipo': 'Generador'},
        {'nombretipo': 'Compresor'},
        {'nombretipo': 'Bomba'}
    ]
    
    tipos = {}
    for tipo_data in tipos_data:
        tipo, created = TiposEquipo.objects.get_or_create(
            nombretipo=tipo_data['nombretipo'],
            defaults=tipo_data
        )
        tipos[tipo_data['nombretipo']] = tipo
        print(f"  ✅ Tipo: {tipo.nombretipo}")
    
    return tipos


def crear_estados_equipo():
    """Crear estados de equipo"""
    print("🔧 Creando estados de equipo...")
    
    estados_data = [
        {'nombreestado': 'Activo'},
        {'nombreestado': 'En Mantenimiento'},
        {'nombreestado': 'Fuera de Servicio'},
        {'nombreestado': 'Disponible'},
        {'nombreestado': 'En Operación'}
    ]
    
    estados = {}
    for estado_data in estados_data:
        estado, created = EstadosEquipo.objects.get_or_create(
            nombreestado=estado_data['nombreestado'],
            defaults=estado_data
        )
        estados[estado_data['nombreestado']] = estado
        print(f"  ✅ Estado: {estado.nombreestado}")
    
    return estados


def crear_faenas():
    """Crear faenas"""
    print("🔧 Creando faenas...")
    
    faenas_data = [
        {'nombrefaena': 'Faena Norte', 'ubicacion': 'Región de Antofagasta', 'activa': True},
        {'nombrefaena': 'Faena Sur', 'ubicacion': 'Región de Atacama', 'activa': True},
        {'nombrefaena': 'Faena Central', 'ubicacion': 'Región Metropolitana', 'activa': True},
        {'nombrefaena': 'Faena Este', 'ubicacion': 'Región de Valparaíso', 'activa': False}
    ]
    
    faenas = {}
    for faena_data in faenas_data:
        faena, created = Faenas.objects.get_or_create(
            nombrefaena=faena_data['nombrefaena'],
            defaults=faena_data
        )
        faenas[faena_data['nombrefaena']] = faena
        print(f"  ✅ Faena: {faena.nombrefaena}")
    
    return faenas


def crear_equipos(tipos, estados, faenas):
    """Crear equipos"""
    print("🔧 Creando equipos...")
    
    marcas = ['Caterpillar', 'Komatsu', 'Volvo', 'Liebherr', 'Hitachi', 'JCB', 'Case']
    modelos = ['320D', 'PC200', 'EC210', 'L150E', 'EX200', 'CX130', '580SN']
    
    equipos_creados = []
    
    for i in range(50):  # Crear 50 equipos
        tipo = random.choice(list(tipos.values()))
        estado = random.choice(list(estados.values()))
        faena = random.choice(list(faenas.values()))
        marca = random.choice(marcas)
        modelo = random.choice(modelos)
        
        equipo_data = {
            'codigointerno': f'EQ{i+1:03d}',
            'nombreequipo': f'{marca} {modelo} {i+1}',
            'marca': marca,
            'modelo': modelo,
            'numeroserie': f'SN{random.randint(100000, 999999)}',
            'aniofabricacion': random.randint(2015, 2023),
            'idtipoequipo': tipo,
            'idestadoactual': estado,
            'idfaena': faena,
            'horometro': random.randint(100, 10000),
            'observaciones': f'Equipo {i+1} - Estado: {estado.nombreestado}'
        }
        
        equipo, created = Equipos.objects.get_or_create(
            codigointerno=equipo_data['codigointerno'],
            defaults=equipo_data
        )
        equipos_creados.append(equipo)
        print(f"  ✅ Equipo: {equipo.nombreequipo}")
    
    return equipos_creados


def crear_estados_orden_trabajo():
    """Crear estados de orden de trabajo"""
    print("🔧 Creando estados de orden de trabajo...")
    
    estados_data = [
        {'nombreestadoot': 'Pendiente'},
        {'nombreestadoot': 'En Proceso'},
        {'nombreestadoot': 'Completada'},
        {'nombreestadoot': 'Cancelada'},
        {'nombreestadoot': 'En Espera de Repuestos'}
    ]
    
    estados = {}
    for estado_data in estados_data:
        estado, created = EstadosOrdenTrabajo.objects.get_or_create(
            nombreestadoot=estado_data['nombreestadoot'],
            defaults=estado_data
        )
        estados[estado_data['nombreestadoot']] = estado
        print(f"  ✅ Estado OT: {estado.nombreestadoot}")
    
    return estados


def crear_tipos_mantenimiento_ot():
    """Crear tipos de mantenimiento de OT"""
    print("🔧 Creando tipos de mantenimiento OT...")
    
    tipos_data = [
        {'nombretipomantenimientoot': 'Correctivo'},
        {'nombretipomantenimientoot': 'Preventivo'},
        {'nombretipomantenimientoot': 'Predictivo'},
        {'nombretipomantenimientoot': 'Modificativo'},
        {'nombretipomantenimientoot': 'Inspección'}
    ]
    
    tipos = {}
    for tipo_data in tipos_data:
        tipo, created = TiposMantenimientoOT.objects.get_or_create(
            nombretipomantenimientoot=tipo_data['nombretipomantenimientoot'],
            defaults=tipo_data
        )
        tipos[tipo_data['nombretipomantenimientoot']] = tipo
        print(f"  ✅ Tipo Mantenimiento: {tipo.nombretipomantenimientoot}")
    
    return tipos


def crear_ordenes_trabajo(equipos, usuarios, estados, tipos_mantenimiento):
    """Crear órdenes de trabajo"""
    print("🔧 Creando órdenes de trabajo...")
    
    problemas = [
        'Falla en motor principal',
        'Pérdida de aceite hidráulico',
        'Desgaste excesivo en cuchilla',
        'Problema en sistema eléctrico',
        'Falla en transmisión',
        'Desgaste en neumáticos',
        'Problema en sistema de refrigeración',
        'Falla en frenos',
        'Desgaste en cadena',
        'Problema en sistema hidráulico'
    ]
    
    prioridades = ['Alta', 'Media', 'Baja']
    
    ordenes_creadas = []
    
    for i in range(100):  # Crear 100 órdenes
        equipo = random.choice(equipos)
        estado = random.choice(list(estados.values()))
        tipo_mantenimiento = random.choice(list(tipos_mantenimiento.values()))
        solicitante = random.choice(list(usuarios.values()))
        tecnico = random.choice(list(usuarios.values()))
        
        # Fecha de creación aleatoria en los últimos 90 días
        fecha_creacion = datetime.now() - timedelta(days=random.randint(0, 90))
        
        orden_data = {
            'numeroot': f'OT-{equipo.codigointerno}-{i+1:04d}',
            'descripcionproblemareportado': random.choice(problemas),
            'prioridad': random.choice(prioridades),
            'idequipo': equipo,
            'idsolicitante': solicitante.user,
            'idtecnicoasignado': tecnico.user,
            'idestadoot': estado,
            'idtipomantenimientoot': tipo_mantenimiento,
            'fechacreacionot': fecha_creacion,
            'horometro': equipo.horometro + random.randint(0, 1000),
            'observacionesfinales': f'Orden {i+1} - {estado.nombreestadoot}'
        }
        
        # Si está completada, agregar fecha de completado
        if estado.nombreestadoot == 'Completada':
            orden_data['fechacompletado'] = fecha_creacion + timedelta(days=random.randint(1, 30))
            orden_data['tiempototalminutos'] = random.randint(60, 480)  # 1-8 horas
        
        orden, created = OrdenesTrabajo.objects.get_or_create(
            numeroot=orden_data['numeroot'],
            defaults=orden_data
        )
        ordenes_creadas.append(orden)
        print(f"  ✅ Orden: {orden.numeroot}")
    
    return ordenes_creadas


def crear_tipos_tarea():
    """Crear tipos de tarea"""
    print("🔧 Creando tipos de tarea...")
    
    tipos_data = [
        {'nombretipotarea': 'Inspección'},
        {'nombretipotarea': 'Limpieza'},
        {'nombretipotarea': 'Lubricación'},
        {'nombretipotarea': 'Ajuste'},
        {'nombretipotarea': 'Reemplazo'},
        {'nombretipotarea': 'Reparación'},
        {'nombretipotarea': 'Calibración'},
        {'nombretipotarea': 'Prueba'}
    ]
    
    tipos = {}
    for tipo_data in tipos_data:
        tipo, created = TiposTarea.objects.get_or_create(
            nombretipotarea=tipo_data['nombretipotarea'],
            defaults=tipo_data
        )
        tipos[tipo_data['nombretipotarea']] = tipo
        print(f"  ✅ Tipo Tarea: {tipo.nombretipotarea}")
    
    return tipos


def crear_tareas_estandar(tipos_tarea):
    """Crear tareas estándar"""
    print("🔧 Creando tareas estándar...")
    
    tareas_data = [
        {'nombretarea': 'Inspección visual general', 'descripcion': 'Revisión visual completa del equipo', 'tiempoestimadominutos': 30, 'tipo': 'Inspección'},
        {'nombretarea': 'Limpieza exterior', 'descripcion': 'Limpieza general del exterior del equipo', 'tiempoestimadominutos': 45, 'tipo': 'Limpieza'},
        {'nombretarea': 'Cambio de aceite motor', 'descripcion': 'Cambio de aceite del motor principal', 'tiempoestimadominutos': 120, 'tipo': 'Reemplazo'},
        {'nombretarea': 'Lubricación de puntos', 'descripcion': 'Lubricación de todos los puntos de engrase', 'tiempoestimadominutos': 60, 'tipo': 'Lubricación'},
        {'nombretarea': 'Ajuste de frenos', 'descripcion': 'Ajuste y verificación del sistema de frenos', 'tiempoestimadominutos': 90, 'tipo': 'Ajuste'},
        {'nombretarea': 'Reemplazo de filtros', 'descripcion': 'Cambio de filtros de aire y combustible', 'tiempoestimadominutos': 75, 'tipo': 'Reemplazo'},
        {'nombretarea': 'Prueba de funcionamiento', 'descripcion': 'Prueba general de funcionamiento del equipo', 'tiempoestimadominutos': 45, 'tipo': 'Prueba'},
        {'nombretarea': 'Calibración de sensores', 'descripcion': 'Calibración de sensores y sistemas de monitoreo', 'tiempoestimadominutos': 150, 'tipo': 'Calibración'}
    ]
    
    tareas = {}
    for tarea_data in tareas_data:
        tarea, created = TareasEstandar.objects.get_or_create(
            nombretarea=tarea_data['nombretarea'],
            defaults={
                'descripcion': tarea_data['descripcion'],
                'tiempoestimadominutos': tarea_data['tiempoestimadominutos'],
                'idtipotarea': tipos_tarea[tarea_data['tipo']]
            }
        )
        tareas[tarea_data['nombretarea']] = tarea
        print(f"  ✅ Tarea: {tarea.nombretarea}")
    
    return tareas


def crear_planes_mantenimiento(equipos, tareas):
    """Crear planes de mantenimiento"""
    print("🔧 Creando planes de mantenimiento...")
    
    planes_creados = []
    
    for i, equipo in enumerate(equipos[:20]):  # Crear planes para los primeros 20 equipos
        plan_data = {
            'nombreplan': f'Plan Mantenimiento {equipo.nombreequipo}',
            'descripcionplan': f'Plan de mantenimiento preventivo para {equipo.nombreequipo}',
            'intervalohorometro': random.randint(500, 2000),
            'intervalotiempo': random.randint(30, 90),  # días
            'idequipo': equipo
        }
        
        plan, created = PlanesMantenimiento.objects.get_or_create(
            nombreplan=plan_data['nombreplan'],
            defaults=plan_data
        )
        
        if created:
            # Agregar tareas al plan
            tareas_plan = random.sample(list(tareas.values()), random.randint(3, 6))
            for j, tarea in enumerate(tareas_plan):
                DetallesPlanMantenimiento.objects.create(
                    idplanmantenimiento=plan,
                    idtareaestandar=tarea,
                    orden=j+1
                )
        
        planes_creados.append(plan)
        print(f"  ✅ Plan: {plan.nombreplan}")
    
    return planes_creados


def main():
    """Función principal para cargar todos los datos"""
    print("🚀 Iniciando carga de datos de muestra V2...")
    
    try:
        # Crear datos maestros
        usuarios = crear_usuarios()
        tipos_equipo = crear_tipos_equipo()
        estados_equipo = crear_estados_equipo()
        faenas = crear_faenas()
        
        # Crear equipos
        equipos = crear_equipos(tipos_equipo, estados_equipo, faenas)
        
        # Crear datos de órdenes de trabajo
        estados_ot = crear_estados_orden_trabajo()
        tipos_mantenimiento = crear_tipos_mantenimiento_ot()
        ordenes = crear_ordenes_trabajo(equipos, usuarios, estados_ot, tipos_mantenimiento)
        
        # Crear datos de mantenimiento preventivo
        tipos_tarea = crear_tipos_tarea()
        tareas = crear_tareas_estandar(tipos_tarea)
        planes = crear_planes_mantenimiento(equipos, tareas)
        
        print("\n🎉 ¡Datos de muestra V2 cargados exitosamente!")
        print(f"📊 Resumen:")
        print(f"  - Usuarios: {len(usuarios)}")
        print(f"  - Equipos: {len(equipos)}")
        print(f"  - Órdenes de trabajo: {len(ordenes)}")
        print(f"  - Planes de mantenimiento: {len(planes)}")
        print(f"  - Tareas estándar: {len(tareas)}")
        
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
