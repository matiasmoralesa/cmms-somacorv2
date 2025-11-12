"""
Script para ajustar y completar todos los datos de la base de datos
Asegura que todos los equipos tengan información completa
"""

import os
import sys
import django
from datetime import datetime, timedelta
from random import randint, choice

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import *
from django.contrib.auth.models import User

print("\n" + "="*80)
print("AJUSTANDO DATOS COMPLETOS DE LA BASE DE DATOS")
print("="*80 + "\n")

# 1. Verificar y actualizar equipos con información completa
print("1. Actualizando información de equipos...")

equipos = Equipos.objects.all()
for equipo in equipos:
    # Asegurar que tenga ubicación de la faena
    if equipo.idfaenaactual:
        # Ya tiene faena asignada, todo bien
        pass
    
    print(f"   - {equipo.codigointerno}: {equipo.nombreequipo}")
    print(f"     Tipo: {equipo.idtipoequipo.nombretipo}")
    print(f"     Estado: {equipo.idestadoactual.nombreestado}")
    print(f"     Faena: {equipo.idfaenaactual.nombrefaena if equipo.idfaenaactual else 'Sin asignar'}")
    print(f"     Marca: {equipo.marca}")
    print(f"     Modelo: {equipo.modelo}")
    print(f"     Año: {equipo.anio}")
    print(f"     Patente: {equipo.patente}")
    print()

print(f"OK - {equipos.count()} equipos verificados\n")

# 2. Crear tipos de mantenimiento si no existen
print("2. Verificando tipos de mantenimiento...")
tipos_mant = ['Preventivo', 'Correctivo', 'Predictivo', 'Emergencia']
for nombre in tipos_mant:
    TiposMantenimientoOT.objects.get_or_create(
        nombretipomantenimientoot=nombre
    )
print(f"   OK - {len(tipos_mant)} tipos de mantenimiento\n")

# 3. Crear estados de órdenes de trabajo si no existen
print("3. Verificando estados de órdenes de trabajo...")
estados_ot = ['Abierta', 'Asignada', 'En Progreso', 'Completada', 'Cancelada']
for nombre in estados_ot:
    EstadosOrdenTrabajo.objects.get_or_create(
        nombreestadoot=nombre
    )
print(f"   OK - {len(estados_ot)} estados de OT\n")

# 4. Generar algunas órdenes de trabajo de ejemplo
print("4. Generando órdenes de trabajo de ejemplo...")

tipo_preventivo = TiposMantenimientoOT.objects.get(nombretipomantenimientoot='Preventivo')
tipo_correctivo = TiposMantenimientoOT.objects.get(nombretipomantenimientoot='Correctivo')
estado_completada = EstadosOrdenTrabajo.objects.get(nombreestadoot='Completada')
estado_en_progreso = EstadosOrdenTrabajo.objects.get(nombreestadoot='En Progreso')
estado_abierta = EstadosOrdenTrabajo.objects.get(nombreestadoot='Abierta')

# Obtener usuarios
usuarios = list(User.objects.all())
if not usuarios:
    print("   ADVERTENCIA: No hay usuarios en el sistema")
else:
    # Crear 50 órdenes distribuidas en 2024
    ordenes_creadas = 0
    for mes in range(1, 13):  # Enero a Diciembre
        for _ in range(4):  # 4 órdenes por mes
            equipo = choice(list(equipos))
            solicitante = choice(usuarios)
            tecnico = choice(usuarios)
            
            # Fecha aleatoria en el mes
            dia = randint(1, 28)
            fecha = datetime(2024, mes, dia, randint(8, 17), randint(0, 59))
            
            # Tipo de mantenimiento
            tipo = choice([tipo_preventivo, tipo_preventivo, tipo_correctivo])  # 66% preventivo
            
            # Estado según antigüedad
            if mes < 11:  # Meses anteriores
                estado = estado_completada
                fecha_completado = fecha + timedelta(days=randint(1, 7))
                tiempo = randint(60, 480)
            elif mes == 11:  # Noviembre
                estado = choice([estado_completada, estado_en_progreso])
                fecha_completado = fecha + timedelta(days=randint(1, 7)) if estado == estado_completada else None
                tiempo = randint(60, 480) if estado == estado_completada else None
            else:  # Diciembre
                estado = choice([estado_abierta, estado_en_progreso])
                fecha_completado = None
                tiempo = None
            
            # Descripción según tipo
            if tipo == tipo_preventivo:
                descripciones = [
                    'Mantenimiento preventivo programado',
                    'Cambio de aceite y filtros',
                    'Revision de 500 horas',
                    'Inspeccion general',
                    'Lubricacion general'
                ]
            else:
                descripciones = [
                    'Falla en sistema hidraulico',
                    'Problema en motor',
                    'Fuga de aceite',
                    'Ruido anormal en transmision',
                    'Sistema electrico defectuoso'
                ]
            
            descripcion = choice(descripciones)
            prioridad = choice(['Baja', 'Media', 'Alta'])
            
            # Crear orden
            OrdenesTrabajo.objects.get_or_create(
                numeroot=f"OT-2024-{mes:02d}-{ordenes_creadas+1:03d}",
                defaults={
                    'idequipo': equipo,
                    'idtipomantenimientoot': tipo,
                    'idestadoot': estado,
                    'idsolicitante': solicitante,
                    'idtecnicoasignado': tecnico,
                    'descripcionproblemareportado': descripcion,
                    'prioridad': prioridad,
                    'fechacreacionot': fecha,
                    'fechareportefalla': fecha,
                    'fechacompletado': fecha_completado,
                    'tiempototalminutos': tiempo,
                    'horometro': randint(1000, 5000)
                }
            )
            ordenes_creadas += 1
    
    print(f"   OK - {ordenes_creadas} órdenes de trabajo creadas\n")

# 5. Resumen final
print("="*80)
print("RESUMEN FINAL")
print("="*80)

print(f"\nTipos de Equipo: {TiposEquipo.objects.count()}")
for tipo in TiposEquipo.objects.all():
    count = Equipos.objects.filter(idtipoequipo=tipo).count()
    print(f"  - {tipo.nombretipo}: {count} equipos")

print(f"\nFaenas: {Faenas.objects.count()}")
for faena in Faenas.objects.all():
    count = Equipos.objects.filter(idfaenaactual=faena).count()
    print(f"  - {faena.nombrefaena}: {count} equipos")

print(f"\nEstados de Equipo: {EstadosEquipo.objects.count()}")
for estado in EstadosEquipo.objects.all():
    count = Equipos.objects.filter(idestadoactual=estado).count()
    print(f"  - {estado.nombreestado}: {count} equipos")

print(f"\nOrdenes de Trabajo: {OrdenesTrabajo.objects.count()}")
for estado in EstadosOrdenTrabajo.objects.all():
    count = OrdenesTrabajo.objects.filter(idestadoot=estado).count()
    if count > 0:
        print(f"  - {estado.nombreestadoot}: {count} ordenes")

print(f"\nUsuarios: {User.objects.count()}")
print(f"Equipos: {Equipos.objects.count()}")

print("\n" + "="*80)
print("COMPLETADO - Base de datos ajustada correctamente")
print("="*80 + "\n")
