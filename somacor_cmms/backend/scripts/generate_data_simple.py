#!/usr/bin/env python
"""
Script simplificado para generar datos masivos
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

fake = Faker('es_ES')

def generate_data():
    print("🚀 Generando datos masivos para el sistema...")
    
    # Obtener datos existentes
    faenas = list(Faenas.objects.all())
    tipos_equipo = list(TiposEquipo.objects.all())
    estados_equipo = list(EstadosEquipo.objects.all())
    roles = list(Roles.objects.all())
    
    if not faenas:
        print("❌ No hay faenas. Ejecuta primero create_simple_data.py")
        return
    
    created_counts = {'equipos': 0, 'usuarios': 0, 'ordenes': 0}
    
    # 1. CREAR MÁS EQUIPOS (200 adicionales)
    print("🚜 Creando equipos adicionales...")
    marcas = ['Caterpillar', 'Komatsu', 'Volvo', 'JCB', 'Case', 'Liebherr', 'Hitachi', 'Doosan']
    
    equipos_existentes = Equipos.objects.count()
    for i in range(equipos_existentes + 1, equipos_existentes + 201):
        tipo_equipo = random.choice(tipos_equipo)
        marca = random.choice(marcas)
        
        equipo = Equipos.objects.create(
            nombreequipo=f"{tipo_equipo.nombretipo} {marca}-{i:03d}",
            codigointerno=f"{marca[:3].upper()}-{i:03d}",
            marca=marca,
            modelo=f"{random.choice(['200', '300', '400', '500'])}{random.choice(['D', 'L', 'X'])}",
            anio=random.randint(2015, 2024),
            patente=fake.license_plate()[:6],
            idtipoequipo=tipo_equipo,
            idestadoactual=random.choice(estados_equipo),
            idfaenaactual=random.choice(faenas),
            activo=random.choice([True, True, True, False])
        )
        created_counts['equipos'] += 1
    
    # 2. CREAR MÁS USUARIOS (40 adicionales)
    print("👥 Creando usuarios adicionales...")
    usuarios_existentes = User.objects.count()
    
    for i in range(usuarios_existentes + 1, usuarios_existentes + 41):
        username = f"user{i:03d}"
        
        # Usuario Django
        django_user = User.objects.create(
            username=username,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            is_active=True
        )
        django_user.set_password('password123')
        django_user.save()
        
        # Perfil CMMS
        if roles:
            Usuarios.objects.create(
                user=django_user,
                idrol=random.choice(roles),
                departamento=random.choice(['Mantenimiento', 'Operaciones', 'Administración'])
            )
        
        created_counts['usuarios'] += 1
    
    # 3. CREAR TIPOS Y ESTADOS PARA OT
    tipos_mantenimiento = []
    tipos_data = ['Preventivo', 'Correctivo', 'Predictivo', 'Emergencia']
    for i, nombre in enumerate(tipos_data, 1):
        tipo, _ = TiposMantenimientoOT.objects.get_or_create(
            nombretipomantenimientoot=nombre,
            defaults={'idtipomantenimientoot': i}
        )
        tipos_mantenimiento.append(tipo)
    
    estados_ot = []
    estados_data = ['Abierta', 'Asignada', 'En Progreso', 'Completada', 'Cancelada']
    for i, nombre in enumerate(estados_data, 1):
        estado, _ = EstadosOrdenTrabajo.objects.get_or_create(
            nombreestadoot=nombre,
            defaults={'idestadoot': i}
        )
        estados_ot.append(estado)
    
    # 4. CREAR ÓRDENES DE TRABAJO (1500 órdenes)
    print("📋 Creando órdenes de trabajo masivas...")
    
    equipos_list = list(Equipos.objects.all())
    usuarios_list = list(User.objects.all())
    prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
    
    descripciones = [
        'Cambio de aceite y filtros', 'Revisión de frenos', 'Mantenimiento preventivo',
        'Falla en motor', 'Problema hidráulico', 'Avería eléctrica', 'Fuga de aceite',
        'Ruido en transmisión', 'Sobrecalentamiento', 'Pérdida de potencia',
        'Vibración excesiva', 'Falla en frenos', 'Inspección general',
        'Cambio de correas', 'Revisión sistema eléctrico', 'Lubricación general'
    ]
    
    ordenes_existentes = OrdenesTrabajo.objects.count()
    
    for i in range(ordenes_existentes + 1, ordenes_existentes + 1501):
        tipo_mantenimiento = random.choice(tipos_mantenimiento)
        descripcion = random.choice(descripciones)
        
        # Fecha de creación realista (últimos 12 meses)
        fecha_creacion = fake.date_time_between(
            start_date='-12M', 
            end_date='now', 
            tzinfo=timezone.get_current_timezone()
        )
        
        # Estado basado en antigüedad
        dias_desde_creacion = (timezone.now() - fecha_creacion).days
        if dias_desde_creacion > 60:
            estado = random.choice([estados_ot[3], estados_ot[4]])  # Completada o Cancelada
        elif dias_desde_creacion > 14:
            estado = random.choice([estados_ot[2], estados_ot[3]])  # En Progreso o Completada
        else:
            estado = random.choice([estados_ot[0], estados_ot[1], estados_ot[2]])  # Abierta, Asignada, En Progreso
        
        fecha_completado = None
        tiempo_total = None
        if estado.nombreestadoot == 'Completada':
            fecha_completado = fecha_creacion + timedelta(days=random.randint(1, 30))
            tiempo_total = random.randint(30, 480)
        
        orden = OrdenesTrabajo.objects.create(
            numeroot=f"OT-{i:05d}",
            idequipo=random.choice(equipos_list),
            idtipomantenimientoot=tipo_mantenimiento,
            idestadoot=estado,
            idsolicitante=random.choice(usuarios_list),
            idtecnicoasignado=random.choice(usuarios_list) if random.random() > 0.3 else None,
            descripcionproblemareportado=descripcion,
            prioridad=random.choice(prioridades),
            fechacreacionot=fecha_creacion,
            fechacompletado=fecha_completado,
            tiempototalminutos=tiempo_total,
            horometro=random.randint(100, 8000),
            observacionesfinales=fake.text(max_nb_chars=150) if fecha_completado else None
        )
        created_counts['ordenes'] += 1
        
        # Mostrar progreso cada 100 órdenes
        if i % 100 == 0:
            print(f"   📋 Creadas {i - ordenes_existentes} órdenes...")
    
    # RESUMEN
    print(f"\n🎉 GENERACIÓN COMPLETADA!")
    print(f"📊 REGISTROS CREADOS:")
    print(f"   🚜 Equipos: {created_counts['equipos']}")
    print(f"   👥 Usuarios: {created_counts['usuarios']}")
    print(f"   📋 Órdenes de Trabajo: {created_counts['ordenes']}")
    
    total_created = sum(created_counts.values())
    print(f"\n🎯 TOTAL NUEVOS REGISTROS: {total_created}")
    
    # Estadísticas finales
    print(f"\n📈 ESTADÍSTICAS FINALES:")
    print(f"   🚜 Total Equipos: {Equipos.objects.count()}")
    print(f"   👥 Total Usuarios: {User.objects.count()}")
    print(f"   📋 Total Órdenes: {OrdenesTrabajo.objects.count()}")
    print(f"   📍 Total Faenas: {Faenas.objects.count()}")
    
    total_sistema = (Equipos.objects.count() + User.objects.count() + 
                    OrdenesTrabajo.objects.count() + Faenas.objects.count())
    print(f"\n🎊 TOTAL REGISTROS EN SISTEMA: {total_sistema}")

if __name__ == '__main__':
    generate_data()