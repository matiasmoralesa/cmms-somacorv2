#!/usr/bin/env python
"""
Script para generar solo órdenes de trabajo masivas usando datos existentes
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

def generate_orders():
    print("🚀 Generando órdenes de trabajo masivas...")
    
    # Obtener datos existentes
    equipos = list(Equipos.objects.all())
    usuarios = list(User.objects.all())
    tipos_mantenimiento = list(TiposMantenimientoOT.objects.all())
    estados_ot = list(EstadosOrdenTrabajo.objects.all())
    
    if not equipos or not usuarios or not tipos_mantenimiento or not estados_ot:
        print("❌ Faltan datos básicos. Ejecuta primero create_simple_orders.py")
        return
    
    print(f"📊 Datos disponibles:")
    print(f"   🚜 Equipos: {len(equipos)}")
    print(f"   👥 Usuarios: {len(usuarios)}")
    print(f"   🔧 Tipos Mantenimiento: {len(tipos_mantenimiento)}")
    print(f"   📋 Estados OT: {len(estados_ot)}")
    
    # Descripciones realistas
    descripciones_preventivo = [
        'Mantenimiento preventivo 250 horas', 'Cambio de aceite motor y filtros',
        'Revisión sistema hidráulico', 'Inspección frenos y dirección',
        'Mantenimiento 500 horas', 'Cambio filtro aire y combustible',
        'Lubricación puntos de engrase', 'Revisión sistema eléctrico',
        'Cambio correas y mangueras', 'Inspección neumáticos',
        'Mantenimiento 1000 horas', 'Calibración sistema hidráulico'
    ]
    
    descripciones_correctivo = [
        'Falla en motor - pérdida de potencia', 'Problema sistema hidráulico - fuga',
        'Avería sistema eléctrico', 'Falla en transmisión - ruidos extraños',
        'Sobrecalentamiento motor', 'Problema en frenos - pérdida eficacia',
        'Vibración excesiva en cabina', 'Fuga aceite motor',
        'Falla bomba hidráulica', 'Problema arranque motor',
        'Avería sistema aire acondicionado', 'Falla en alternador'
    ]
    
    descripciones_emergencia = [
        'EMERGENCIA: Motor sobrecalentado - detener operación',
        'URGENTE: Falla frenos - equipo inseguro',
        'CRÍTICO: Fuga combustible - riesgo incendio',
        'EMERGENCIA: Falla dirección - pérdida control',
        'URGENTE: Falla sistema hidráulico - brazo caído'
    ]
    
    prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
    
    # Generar 1800 órdenes
    ordenes_existentes = OrdenesTrabajo.objects.count()
    print(f"📋 Órdenes existentes: {ordenes_existentes}")
    print(f"📋 Generando 1800 órdenes adicionales...")
    
    created_count = 0
    
    for i in range(1, 1801):
        numero_ot = ordenes_existentes + i
        
        # Seleccionar tipo de mantenimiento
        tipo_mantenimiento = random.choice(tipos_mantenimiento)
        
        # Seleccionar descripción según el tipo
        if tipo_mantenimiento.nombretipomantenimientoot == 'Preventivo':
            descripcion = random.choice(descripciones_preventivo)
            prioridad = random.choice(['Baja', 'Media'])
        elif tipo_mantenimiento.nombretipomantenimientoot == 'Emergencia':
            descripcion = random.choice(descripciones_emergencia)
            prioridad = 'Crítica'
        else:
            descripcion = random.choice(descripciones_correctivo)
            prioridad = random.choice(['Media', 'Alta', 'Crítica'])
        
        # Fecha de creación realista (últimos 18 meses)
        fecha_creacion = fake.date_time_between(
            start_date='-18M', 
            end_date='now', 
            tzinfo=timezone.get_current_timezone()
        )
        
        # Estado basado en antigüedad y tipo
        dias_desde_creacion = (timezone.now() - fecha_creacion).days
        
        if dias_desde_creacion > 90:
            # Órdenes muy antiguas - mayoría completadas
            estado = random.choice([
                estados_ot[3] if len(estados_ot) > 3 else estados_ot[-1],  # Completada
                estados_ot[3] if len(estados_ot) > 3 else estados_ot[-1],  # Completada
                estados_ot[4] if len(estados_ot) > 4 else estados_ot[-1]   # Cancelada
            ])
        elif dias_desde_creacion > 30:
            # Órdenes medianas - mix de estados
            estado = random.choice([
                estados_ot[2] if len(estados_ot) > 2 else estados_ot[-1],  # En Progreso
                estados_ot[3] if len(estados_ot) > 3 else estados_ot[-1],  # Completada
                estados_ot[3] if len(estados_ot) > 3 else estados_ot[-1]   # Completada
            ])
        else:
            # Órdenes recientes - mayoría activas
            estado = random.choice([
                estados_ot[0],  # Abierta
                estados_ot[1] if len(estados_ot) > 1 else estados_ot[0],  # Asignada
                estados_ot[2] if len(estados_ot) > 2 else estados_ot[0]   # En Progreso
            ])
        
        # Fechas y tiempos según el estado
        fecha_completado = None
        tiempo_total = None
        observaciones = None
        
        if estado.nombreestadoot == 'Completada':
            fecha_completado = fecha_creacion + timedelta(
                days=random.randint(1, 45),
                hours=random.randint(1, 23)
            )
            tiempo_total = random.randint(30, 600)  # 30 min a 10 horas
            observaciones = fake.text(max_nb_chars=200)
        
        # Crear la orden
        try:
            orden = OrdenesTrabajo.objects.create(
                numeroot=f"OT-{numero_ot:05d}",
                idequipo=random.choice(equipos),
                idtipomantenimientoot=tipo_mantenimiento,
                idestadoot=estado,
                idsolicitante=random.choice(usuarios),
                idtecnicoasignado=random.choice(usuarios) if random.random() > 0.2 else None,
                descripcionproblemareportado=descripcion,
                prioridad=prioridad,
                fechacreacionot=fecha_creacion,
                fechacompletado=fecha_completado,
                tiempototalminutos=tiempo_total,
                horometro=random.randint(100, 12000),
                observacionesfinales=observaciones
            )
            created_count += 1
            
            # Mostrar progreso cada 200 órdenes
            if i % 200 == 0:
                print(f"   📋 Creadas {i} órdenes...")
                
        except Exception as e:
            print(f"❌ Error creando orden {numero_ot}: {e}")
    
    print(f"\n🎉 GENERACIÓN COMPLETADA!")
    print(f"📊 ÓRDENES CREADAS: {created_count}")
    print(f"📊 TOTAL ÓRDENES EN SISTEMA: {OrdenesTrabajo.objects.count()}")
    
    # Estadísticas por estado
    print(f"\n📈 DISTRIBUCIÓN POR ESTADO:")
    for estado in estados_ot:
        count = OrdenesTrabajo.objects.filter(idestadoot=estado).count()
        print(f"   📋 {estado.nombreestadoot}: {count}")
    
    # Estadísticas por tipo
    print(f"\n🔧 DISTRIBUCIÓN POR TIPO:")
    for tipo in tipos_mantenimiento:
        count = OrdenesTrabajo.objects.filter(idtipomantenimientoot=tipo).count()
        print(f"   🔧 {tipo.nombretipomantenimientoot}: {count}")
    
    # Estadísticas por prioridad
    print(f"\n⚡ DISTRIBUCIÓN POR PRIORIDAD:")
    for prioridad in ['Baja', 'Media', 'Alta', 'Crítica']:
        count = OrdenesTrabajo.objects.filter(prioridad=prioridad).count()
        print(f"   ⚡ {prioridad}: {count}")

if __name__ == '__main__':
    generate_orders()