"""
Script para inyectar 10,000 datos realistas en la base de datos
Con distribución realista en los últimos 2 meses
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random
import math

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from django.contrib.auth.models import User
from cmms_api.models import *

def get_realistic_date_distribution():
    """Generar fechas realistas con más actividad en los últimos 2 meses"""
    today = datetime.now()
    two_months_ago = today - timedelta(days=60)
    
    # Distribución: 80% en últimos 2 meses, 20% en el resto del año
    dates = []
    
    # Últimos 2 meses (máximo 150 por mes = 300 total)
    for i in range(300):
        # Distribución más realista: más actividad en días laborales
        days_ago = random.randint(0, 60)
        base_date = today - timedelta(days=days_ago)
        
        # Ajustar para días laborales (lunes a viernes)
        if base_date.weekday() >= 5:  # Sábado o domingo
            if random.random() < 0.3:  # 30% de actividad en fines de semana
                base_date = base_date - timedelta(days=random.randint(1, 2))
        
        # Ajustar hora para ser más realista (8 AM - 6 PM)
        hour = random.randint(8, 18)
        minute = random.randint(0, 59)
        realistic_date = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        dates.append(realistic_date)
    
    # Resto del año (distribución más dispersa)
    for i in range(700):
        days_ago = random.randint(60, 365)
        base_date = today - timedelta(days=days_ago)
        
        # Ajustar hora para ser más realista
        hour = random.randint(7, 19)
        minute = random.randint(0, 59)
        realistic_date = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        dates.append(realistic_date)
    
    # Mezclar las fechas
    random.shuffle(dates)
    return dates

def create_additional_users():
    """Crear usuarios adicionales para hacer el sistema más realista"""
    print("Creando usuarios adicionales...")
    
    # Obtener roles existentes
    roles = {rol.nombrerol: rol for rol in Roles.objects.all()}
    
    # Crear usuarios adicionales
    usuarios_adicionales = [
        # Supervisores
        {'username': 'supervisor2', 'email': 'supervisor2@somacor.com', 'first_name': 'Roberto', 'last_name': 'Silva', 'rol': 'Supervisor'},
        {'username': 'supervisor3', 'email': 'supervisor3@somacor.com', 'first_name': 'Patricia', 'last_name': 'Morales', 'rol': 'Supervisor'},
        
        # Técnicos
        {'username': 'tecnico3', 'email': 'tecnico3@somacor.com', 'first_name': 'Luis', 'last_name': 'Hernandez', 'rol': 'Tecnico'},
        {'username': 'tecnico4', 'email': 'tecnico4@somacor.com', 'first_name': 'Carmen', 'last_name': 'Vargas', 'rol': 'Tecnico'},
        {'username': 'tecnico5', 'email': 'tecnico5@somacor.com', 'first_name': 'Diego', 'last_name': 'Ramirez', 'rol': 'Tecnico'},
        {'username': 'tecnico6', 'email': 'tecnico6@somacor.com', 'first_name': 'Sofia', 'last_name': 'Castillo', 'rol': 'Tecnico'},
        
        # Operadores
        {'username': 'operador2', 'email': 'operador2@somacor.com', 'first_name': 'Miguel', 'last_name': 'Torres', 'rol': 'Operador'},
        {'username': 'operador3', 'email': 'operador3@somacor.com', 'first_name': 'Elena', 'last_name': 'Jimenez', 'rol': 'Operador'},
        
        # Planificadores
        {'username': 'planificador2', 'email': 'planificador2@somacor.com', 'first_name': 'Fernando', 'last_name': 'Rojas', 'rol': 'Planificador'},
    ]
    
    usuarios_creados = []
    for user_data in usuarios_adicionales:
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
        usuarios_creados.append(usuario_cmms)
        print(f"  Usuario: {user.username} ({user_data['rol']})")
    
    return usuarios_creados

def create_additional_equipment():
    """Crear equipos adicionales para llegar a ~200 equipos"""
    print("Creando equipos adicionales...")
    
    # Obtener datos existentes
    tipos = list(TiposEquipo.objects.all())
    estados = list(EstadosEquipo.objects.all())
    faenas = list(Faenas.objects.all())
    
    marcas = ['Caterpillar', 'Komatsu', 'Volvo', 'Liebherr', 'Hitachi', 'JCB', 'Case', 'John Deere', 'New Holland', 'Bobcat']
    modelos = ['320D', 'PC200', 'EC210', 'L150E', 'EX200', 'CX130', '580SN', 'D6T', 'WA320', 'ZX210']
    
    equipos_creados = []
    current_count = Equipos.objects.count()
    
    # Crear hasta 200 equipos totales
    for i in range(200 - current_count):
        tipo = random.choice(tipos)
        estado = random.choice(estados)
        faena = random.choice(faenas)
        marca = random.choice(marcas)
        modelo = random.choice(modelos)
        
        # Hacer algunos equipos más críticos (con más mantenimiento)
        is_critical = random.random() < 0.2  # 20% de equipos críticos
        
        equipo_data = {
            'codigointerno': f'EQ{i+current_count+1:04d}',
            'nombreequipo': f'{marca} {modelo} {i+current_count+1}',
            'marca': marca,
            'modelo': modelo,
            'anio': random.randint(2010, 2023),
            'patente': f'PAT{i+current_count+1:05d}',
            'idtipoequipo': tipo,
            'idestadoactual': estado,
            'idfaenaactual': faena,
            'activo': True
        }
        
        # Equipos críticos tienen más probabilidad de estar en mantenimiento
        if is_critical and random.random() < 0.4:
            mantenimiento_estado = EstadosEquipo.objects.filter(nombreestado__icontains='mantenimiento').first()
            if mantenimiento_estado:
                equipo_data['idestadoactual'] = mantenimiento_estado
        
        equipo, created = Equipos.objects.get_or_create(
            codigointerno=equipo_data['codigointerno'],
            defaults=equipo_data
        )
        equipos_creados.append(equipo)
        
        if (i + 1) % 50 == 0:
            print(f"  Creados {i + 1} equipos adicionales...")
    
    return equipos_creados

def create_massive_work_orders(equipos, usuarios, fechas):
    """Crear órdenes de trabajo masivas con distribución realista"""
    print("Creando órdenes de trabajo masivas...")
    
    # Obtener datos existentes
    estados = list(EstadosOrdenTrabajo.objects.all())
    tipos_mantenimiento = list(TiposMantenimientoOT.objects.all())
    
    # Problemas más comunes (con pesos)
    problemas_comunes = [
        ('Falla en motor principal', 0.15),
        ('Pérdida de aceite hidráulico', 0.12),
        ('Desgaste excesivo en cuchilla', 0.10),
        ('Problema en sistema eléctrico', 0.08),
        ('Falla en transmisión', 0.08),
        ('Desgaste en neumáticos', 0.07),
        ('Problema en sistema de refrigeración', 0.06),
        ('Falla en frenos', 0.06),
        ('Desgaste en cadena', 0.05),
        ('Problema en sistema hidráulico', 0.05),
        ('Fuga de combustible', 0.04),
        ('Problema en dirección', 0.04),
        ('Desgaste en filtros', 0.03),
        ('Problema en alternador', 0.03),
        ('Falla en compresor', 0.02),
        ('Problema en bomba', 0.02),
    ]
    
    # Prioridades con distribución realista
    prioridades = [
        ('Alta', 0.20),
        ('Media', 0.60),
        ('Baja', 0.20),
    ]
    
    ordenes_creadas = []
    
    for i, fecha in enumerate(fechas):
        if i >= 10000:  # Limitar a 10,000 órdenes
            break
            
        equipo = random.choice(equipos)
        estado = random.choice(estados)
        tipo_mantenimiento = random.choice(tipos_mantenimiento)
        solicitante = random.choice(usuarios)
        tecnico = random.choice(usuarios)
        
        # Seleccionar problema basado en peso
        problema = random.choices(
            [p[0] for p in problemas_comunes],
            weights=[p[1] for p in problemas_comunes]
        )[0]
        
        # Seleccionar prioridad basado en peso
        prioridad = random.choices(
            [p[0] for p in prioridades],
            weights=[p[1] for p in prioridades]
        )[0]
        
        # Ajustar prioridad basado en el tipo de problema
        if 'falla' in problema.lower() or 'motor' in problema.lower():
            if random.random() < 0.7:  # 70% de probabilidad de ser alta prioridad
                prioridad = 'Alta'
        
        orden_data = {
            'numeroot': f'OT-{equipo.codigointerno}-{i+1:06d}',
            'descripcionproblemareportado': problema,
            'prioridad': prioridad,
            'idequipo': equipo,
            'idsolicitante': solicitante.user,
            'idtecnicoasignado': tecnico.user,
            'idestadoot': estado,
            'idtipomantenimientoot': tipo_mantenimiento,
            'fechareportefalla': fecha,
            'horometro': random.randint(100, 15000),
        }
        
        # Si está completada, agregar fecha de completado y tiempo
        if estado.nombreestadoot == 'Completada':
            # Tiempo de completado basado en prioridad
            if prioridad == 'Alta':
                completion_hours = random.randint(1, 8)  # 1-8 horas
            elif prioridad == 'Media':
                completion_hours = random.randint(4, 24)  # 4-24 horas
            else:
                completion_hours = random.randint(8, 72)  # 8-72 horas
            
            orden_data['fechacompletado'] = fecha + timedelta(hours=completion_hours)
            orden_data['tiempototalminutos'] = completion_hours * 60
            
            # Agregar observaciones finales
            observaciones = [
                f'Reparación completada exitosamente. Tiempo total: {completion_hours}h',
                f'Trabajo realizado según procedimientos estándar.',
                f'Equipo operativo y listo para uso.',
                f'Mantenimiento preventivo adicional realizado.',
                f'Componentes reemplazados y calibrados.',
            ]
            orden_data['observacionesfinales'] = random.choice(observaciones)
        
        # Si está en proceso, agregar fecha de ejecución
        elif estado.nombreestadoot == 'En Proceso':
            orden_data['fechaejecucion'] = fecha + timedelta(hours=random.randint(1, 12))
        
        orden, created = OrdenesTrabajo.objects.get_or_create(
            numeroot=orden_data['numeroot'],
            defaults=orden_data
        )
        ordenes_creadas.append(orden)
        
        if (i + 1) % 1000 == 0:
            print(f"  Creadas {i + 1} órdenes de trabajo...")
    
    return ordenes_creadas

def create_activities_for_work_orders(ordenes, usuarios):
    """Crear actividades para las órdenes de trabajo"""
    print("Creando actividades para órdenes de trabajo...")
    
    # Obtener tareas estándar
    tareas_estandar = list(TareasEstandar.objects.all())
    
    actividades_creadas = []
    
    # Solo crear actividades para órdenes completadas o en proceso
    ordenes_con_actividades = [ot for ot in ordenes if ot.idestadoot.nombreestadoot in ['Completada', 'En Proceso']]
    
    for orden in ordenes_con_actividades:
        # Entre 1 y 5 actividades por orden
        num_actividades = random.randint(1, 5)
        
        for j in range(num_actividades):
            tarea = random.choice(tareas_estandar) if tareas_estandar else None
            tecnico = random.choice(usuarios)
            
            # Fecha de inicio basada en la fecha de la orden
            fecha_inicio = orden.fechareportefalla + timedelta(hours=random.randint(0, 8))
            
            actividad_data = {
                'idordentrabajo': orden,
                'idtareaestandar': tarea,
                'idtecnico': tecnico.user,
                'fechainicio': fecha_inicio,
                'descripcionactividad': tarea.descripcion if tarea else f'Actividad {j+1} para {orden.numeroot}',
                'estado': random.choice(['En Proceso', 'Completada', 'Pendiente']),
            }
            
            # Si está completada, agregar fecha fin y tiempo real
            if actividad_data['estado'] == 'Completada':
                tiempo_estimado = tarea.tiempoestimadominutos if tarea else 60
                # Tiempo real puede variar ±30% del estimado
                variacion = random.uniform(0.7, 1.3)
                tiempo_real = int(tiempo_estimado * variacion)
                
                actividad_data['fechafin'] = fecha_inicio + timedelta(minutes=tiempo_real)
                actividad_data['tiemporealminutos'] = tiempo_real
                
                observaciones = [
                    'Actividad completada según procedimientos.',
                    'Trabajo realizado sin inconvenientes.',
                    'Se realizó mantenimiento adicional preventivo.',
                    'Componente reemplazado y calibrado.',
                ]
                actividad_data['observaciones'] = random.choice(observaciones)
            
            try:
                actividad = ActividadesOrdenTrabajo.objects.create(**actividad_data)
                actividades_creadas.append(actividad)
            except Exception as e:
                print(f"  Error creando actividad: {e}")
                continue
    
    print(f"  Creadas {len(actividades_creadas)} actividades")
    return actividades_creadas

def main():
    """Función principal para inyectar datos masivos"""
    print("Iniciando inyeccion masiva de datos...")
    
    try:
        # 1. Crear fechas realistas
        print("\nGenerando distribucion de fechas realistas...")
        fechas = get_realistic_date_distribution()
        print(f"  Generadas {len(fechas)} fechas con distribucion realista")
        
        # 2. Crear usuarios adicionales
        usuarios_adicionales = create_additional_users()
        usuarios_existentes = list(Usuarios.objects.all())
        todos_los_usuarios = usuarios_existentes + usuarios_adicionales
        
        # 3. Crear equipos adicionales
        equipos_adicionales = create_additional_equipment()
        equipos_existentes = list(Equipos.objects.all())
        todos_los_equipos = equipos_existentes + equipos_adicionales
        
        # 4. Crear órdenes de trabajo masivas
        ordenes = create_massive_work_orders(todos_los_equipos, todos_los_usuarios, fechas)
        
        # 5. Crear actividades para las órdenes
        actividades = create_activities_for_work_orders(ordenes, todos_los_usuarios)
        
        print("\nInyeccion masiva de datos completada!")
        print(f"Resumen final:")
        print(f"  - Usuarios totales: {len(todos_los_usuarios)}")
        print(f"  - Equipos totales: {len(todos_los_equipos)}")
        print(f"  - Ordenes de trabajo: {len(ordenes)}")
        print(f"  - Actividades: {len(actividades)}")
        print(f"  - Fechas distribuidas: {len(fechas)}")
        
        # Estadisticas de distribucion temporal
        hoy = datetime.now()
        dos_meses_atras = hoy - timedelta(days=60)
        ordenes_recientes = [ot for ot in ordenes if ot.fechareportefalla >= dos_meses_atras]
        
        print(f"\nDistribucion temporal:")
        print(f"  - Ordenes en ultimos 2 meses: {len(ordenes_recientes)}")
        print(f"  - Promedio por mes: {len(ordenes_recientes) // 2}")
        print(f"  - Ordenes historicas: {len(ordenes) - len(ordenes_recientes)}")
        
    except Exception as e:
        print(f"Error en inyeccion masiva: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
