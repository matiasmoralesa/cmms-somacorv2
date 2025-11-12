#!/usr/bin/env python
"""
Script para crear órdenes de trabajo para el año 2025
"""
import os
import django
import sys
from datetime import datetime, timedelta
import random

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import (
    OrdenesTrabajo, Equipos, Usuarios, EstadosOrdenTrabajo,
    TiposMantenimientoOT
)
from django.contrib.auth.models import User

def crear_ordenes_2025():
    """Crear órdenes de trabajo para 2025"""
    
    print("🚀 Creando órdenes de trabajo para 2025...")
    
    # Obtener datos necesarios
    equipos = list(Equipos.objects.all()[:10])
    # Obtener usuarios de Django (User), no de Usuarios
    usuarios_django = list(User.objects.all()[:5])
    estados = list(EstadosOrdenTrabajo.objects.all())
    tipos_mantenimiento = list(TiposMantenimientoOT.objects.all())
    
    if not equipos:
        print("❌ No hay equipos en la base de datos")
        return
    
    if not usuarios_django:
        print("❌ No hay usuarios en la base de datos")
        return
    
    if not estados:
        print("❌ No hay estados de orden de trabajo")
        return
    
    if not tipos_mantenimiento:
        print("❌ No hay tipos de mantenimiento")
        return
    
    # Buscar estados específicos
    estado_completada = next((e for e in estados if 'completada' in e.nombreestadoot.lower()), estados[0])
    estado_en_progreso = next((e for e in estados if 'progreso' in e.nombreestadoot.lower()), estados[0])
    estado_abierta = next((e for e in estados if 'abierta' in e.nombreestadoot.lower()), estados[0])
    
    prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
    descripciones = [
        'Mantenimiento preventivo programado',
        'Cambio de aceite y filtros',
        'Revisión de sistema hidráulico',
        'Inspección general',
        'Lubricación general',
        'Cambio de neumáticos',
        'Reparación de sistema eléctrico',
        'Ajuste de frenos',
        'Revisión de motor',
        'Mantenimiento de transmisión'
    ]
    
    ordenes_creadas = 0
    
    # Crear órdenes para cada mes de 2025
    for mes in range(1, 12):  # Enero a Noviembre
        # Crear entre 5 y 15 órdenes por mes
        num_ordenes = random.randint(5, 15)
        
        for i in range(num_ordenes):
            # Fecha aleatoria dentro del mes
            dia = random.randint(1, 28)
            fecha = datetime(2025, mes, dia, random.randint(8, 17), random.randint(0, 59))
            
            # Seleccionar datos aleatorios
            equipo = random.choice(equipos)
            solicitante = random.choice(usuarios_django)
            tecnico = random.choice(usuarios_django)
            tipo_mant = random.choice(tipos_mantenimiento)
            prioridad = random.choice(prioridades)
            descripcion = random.choice(descripciones)
            
            # 70% completadas, 20% en progreso, 10% abiertas
            rand = random.random()
            if rand < 0.7:
                estado = estado_completada
                fecha_completado = fecha + timedelta(hours=random.randint(2, 48))
            elif rand < 0.9:
                estado = estado_en_progreso
                fecha_completado = None
            else:
                estado = estado_abierta
                fecha_completado = None
            
            # Crear número de OT
            numero_ot = f"OT-2025-{mes:02d}-{ordenes_creadas+1:03d}"
            
            try:
                orden = OrdenesTrabajo.objects.create(
                    numeroot=numero_ot,
                    descripcionproblemareportado=descripcion,
                    prioridad=prioridad,
                    idequipo=equipo,
                    idsolicitante=solicitante,
                    idtecnicoasignado=tecnico,
                    idestadoot=estado,
                    idtipomantenimientoot=tipo_mant,
                    fechareportefalla=fecha,
                    fechacreacionot=fecha,
                    fechacompletado=fecha_completado,
                    horometro=random.randint(1000, 5000),
                    tiempototalminutos=random.randint(60, 480) if fecha_completado else None
                )
                ordenes_creadas += 1
                
                if ordenes_creadas % 10 == 0:
                    print(f"✅ Creadas {ordenes_creadas} órdenes...")
                    
            except Exception as e:
                print(f"❌ Error creando orden: {e}")
    
    print(f"\n🎉 Total de órdenes creadas: {ordenes_creadas}")
    
    # Mostrar resumen por mes
    print("\n📊 Resumen por mes:")
    for mes in range(1, 12):
        total = OrdenesTrabajo.objects.filter(
            fechacreacionot__year=2025,
            fechacreacionot__month=mes
        ).count()
        
        completadas = OrdenesTrabajo.objects.filter(
            fechacreacionot__year=2025,
            fechacreacionot__month=mes,
            idestadoot=estado_completada
        ).count()
        
        meses_nombres = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        print(f"  {meses_nombres[mes]}: {total} órdenes ({completadas} completadas)")

if __name__ == "__main__":
    crear_ordenes_2025()
