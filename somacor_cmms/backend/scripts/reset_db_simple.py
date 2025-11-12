"""
Script simple para limpiar y poblar la base de datos
Sin emojis para compatibilidad con Windows
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import *
from django.contrib.auth.models import User
from django.db import transaction
from datetime import datetime, timedelta
from random import randint, choice

print("\n" + "="*80)
print("LIMPIANDO Y POBLANDO BASE DE DATOS")
print("="*80 + "\n")

# 1. LIMPIAR BASE DE DATOS
print("1. Limpiando base de datos...")
try:
    with transaction.atomic():
        ChecklistCategory.objects.all().delete()
        ChecklistTemplate.objects.all().delete()
        OrdenesTrabajo.objects.all().delete()
        Equipos.objects.all().delete()
        EstadosEquipo.objects.all().delete()
        TiposEquipo.objects.all().delete()
        Faenas.objects.all().delete()
        Usuarios.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Roles.objects.all().delete()
    print("   OK - Base de datos limpiada\n")
except Exception as e:
    print(f"   ERROR: {e}\n")
    sys.exit(1)

# 2. CREAR ROLES
print("2. Creando roles...")
roles_data = ['Administrador', 'Supervisor', 'Tecnico', 'Operador', 'Jefe de Mantencion']
roles = []
for nombre in roles_data:
    rol, _ = Roles.objects.get_or_create(nombrerol=nombre)
    roles.append(rol)
print(f"   OK - {len(roles)} roles creados\n")

# 3. CREAR FAENAS
print("3. Creando faenas...")
faenas_data = [
    {'nombre': 'Faena Central Santiago', 'ciudad': 'Santiago', 'region': 'Metropolitana'},
    {'nombre': 'Faena Norte Antofagasta', 'ciudad': 'Antofagasta', 'region': 'Antofagasta'},
    {'nombre': 'Faena Sur Concepcion', 'ciudad': 'Concepcion', 'region': 'Biobio'}
]
faenas = []
for data in faenas_data:
    faena, _ = Faenas.objects.get_or_create(
        nombrefaena=data['nombre'],
        defaults={'ciudad': data['ciudad'], 'region': data['region'], 'activa': True}
    )
    faenas.append(faena)
print(f"   OK - {len(faenas)} faenas creadas\n")

# 4. CREAR ESTADOS DE EQUIPO
print("4. Creando estados de equipo...")
estados_data = ['Operativo', 'En Mantenimiento', 'Fuera de Servicio', 'En Reparacion', 'Disponible']
estados = []
for nombre in estados_data:
    estado, _ = EstadosEquipo.objects.get_or_create(nombreestado=nombre)
    estados.append(estado)
print(f"   OK - {len(estados)} estados creados\n")

# 5. CREAR TIPOS DE EQUIPO (LOS 5 DEL PROYECTO)
print("5. Creando tipos de equipo...")
tipos_data = [
    'Camionetas',
    'Retroexcavadora',
    'Cargador Frontal',
    'Minicargador',
    'Camion Supersucker'
]
tipos = []
for nombre in tipos_data:
    tipo, _ = TiposEquipo.objects.get_or_create(nombretipo=nombre)
    tipos.append(tipo)
print(f"   OK - {len(tipos)} tipos creados\n")

# 6. CREAR EQUIPOS (20 EQUIPOS)
print("6. Creando equipos...")
estado_operativo = next(e for e in estados if e.nombreestado == 'Operativo')
estado_mantenimiento = next(e for e in estados if e.nombreestado == 'En Mantenimiento')

equipos_data = [
    # CAMIONETAS (6)
    {'tipo': 0, 'codigo': 'CAM-001', 'nombre': 'Toyota Hilux 2020', 'marca': 'Toyota', 'modelo': 'Hilux', 'año': 2020, 'patente': 'BBCD12', 'faena': 0, 'estado': estado_operativo},
    {'tipo': 0, 'codigo': 'CAM-002', 'nombre': 'Ford Ranger 2021', 'marca': 'Ford', 'modelo': 'Ranger XLT', 'año': 2021, 'patente': 'CCDE23', 'faena': 0, 'estado': estado_operativo},
    {'tipo': 0, 'codigo': 'CAM-003', 'nombre': 'Chevrolet S10 2019', 'marca': 'Chevrolet', 'modelo': 'S10', 'año': 2019, 'patente': 'DDEF34', 'faena': 1, 'estado': estado_operativo},
    {'tipo': 0, 'codigo': 'CAM-004', 'nombre': 'Nissan Frontier 2022', 'marca': 'Nissan', 'modelo': 'Frontier', 'año': 2022, 'patente': 'EEFG45', 'faena': 1, 'estado': estado_operativo},
    {'tipo': 0, 'codigo': 'CAM-005', 'nombre': 'Mitsubishi L200 2020', 'marca': 'Mitsubishi', 'modelo': 'L200', 'año': 2020, 'patente': 'FFGH56', 'faena': 2, 'estado': estado_operativo},
    {'tipo': 0, 'codigo': 'CAM-006', 'nombre': 'Toyota Hilux 2018', 'marca': 'Toyota', 'modelo': 'Hilux SR5', 'año': 2018, 'patente': 'GGHI67', 'faena': 2, 'estado': estado_mantenimiento},
    
    # RETROEXCAVADORAS (4)
    {'tipo': 1, 'codigo': 'RETRO-001', 'nombre': 'CAT 420F 2019', 'marca': 'Caterpillar', 'modelo': '420F', 'año': 2019, 'patente': 'HHIJ78', 'faena': 0, 'estado': estado_operativo},
    {'tipo': 1, 'codigo': 'RETRO-002', 'nombre': 'JCB 3CX 2020', 'marca': 'JCB', 'modelo': '3CX', 'año': 2020, 'patente': 'IIJK89', 'faena': 1, 'estado': estado_operativo},
    {'tipo': 1, 'codigo': 'RETRO-003', 'nombre': 'CAT 416F 2018', 'marca': 'Caterpillar', 'modelo': '416F', 'año': 2018, 'patente': 'JJKL90', 'faena': 2, 'estado': estado_operativo},
    {'tipo': 1, 'codigo': 'RETRO-004', 'nombre': 'JCB 4CX 2021', 'marca': 'JCB', 'modelo': '4CX', 'año': 2021, 'patente': 'KKLM01', 'faena': 0, 'estado': estado_mantenimiento},
    
    # CARGADORES FRONTALES (4)
    {'tipo': 2, 'codigo': 'CARG-001', 'nombre': 'CAT 950M 2018', 'marca': 'Caterpillar', 'modelo': '950M', 'año': 2018, 'patente': 'LLMN12', 'faena': 0, 'estado': estado_operativo},
    {'tipo': 2, 'codigo': 'CARG-002', 'nombre': 'Komatsu WA380 2019', 'marca': 'Komatsu', 'modelo': 'WA380-8', 'año': 2019, 'patente': 'MMNO23', 'faena': 1, 'estado': estado_operativo},
    {'tipo': 2, 'codigo': 'CARG-003', 'nombre': 'CAT 966M 2020', 'marca': 'Caterpillar', 'modelo': '966M', 'año': 2020, 'patente': 'NNOP34', 'faena': 1, 'estado': estado_operativo},
    {'tipo': 2, 'codigo': 'CARG-004', 'nombre': 'Volvo L120H 2019', 'marca': 'Volvo', 'modelo': 'L120H', 'año': 2019, 'patente': 'OOPQ45', 'faena': 2, 'estado': estado_operativo},
    
    # MINICARGADORES (4)
    {'tipo': 3, 'codigo': 'MINI-001', 'nombre': 'Bobcat S650 2020', 'marca': 'Bobcat', 'modelo': 'S650', 'año': 2020, 'patente': 'PPQR56', 'faena': 0, 'estado': estado_operativo},
    {'tipo': 3, 'codigo': 'MINI-002', 'nombre': 'CAT 262D 2021', 'marca': 'Caterpillar', 'modelo': '262D', 'año': 2021, 'patente': 'QQRS67', 'faena': 0, 'estado': estado_operativo},
    {'tipo': 3, 'codigo': 'MINI-003', 'nombre': 'Bobcat S770 2019', 'marca': 'Bobcat', 'modelo': 'S770', 'año': 2019, 'patente': 'RRST78', 'faena': 1, 'estado': estado_operativo},
    {'tipo': 3, 'codigo': 'MINI-004', 'nombre': 'JCB 330 2020', 'marca': 'JCB', 'modelo': '330', 'año': 2020, 'patente': 'SSTU89', 'faena': 2, 'estado': estado_operativo},
    
    # CAMIONES SUPERSUCKER (2)
    {'tipo': 4, 'codigo': 'SUPER-001', 'nombre': 'Volvo FMX 500 2019', 'marca': 'Volvo', 'modelo': 'FMX 500', 'año': 2019, 'patente': 'TTUV90', 'faena': 0, 'estado': estado_operativo},
    {'tipo': 4, 'codigo': 'SUPER-002', 'nombre': 'Mercedes Actros 2646 2020', 'marca': 'Mercedes-Benz', 'modelo': 'Actros 2646', 'año': 2020, 'patente': 'UUVW01', 'faena': 1, 'estado': estado_operativo},
]

equipos = []
for data in equipos_data:
    equipo, _ = Equipos.objects.get_or_create(
        codigointerno=data['codigo'],
        defaults={
            'nombreequipo': data['nombre'],
            'marca': data['marca'],
            'modelo': data['modelo'],
            'anio': data['año'],
            'patente': data['patente'],
            'idtipoequipo': tipos[data['tipo']],
            'idfaenaactual': faenas[data['faena']],
            'idestadoactual': data['estado'],
            'activo': True
        }
    )
    equipos.append(equipo)
print(f"   OK - {len(equipos)} equipos creados\n")

# 7. CREAR USUARIOS
print("7. Creando usuarios...")
usuarios_data = [
    {'username': 'admin', 'nombre': 'Admin', 'apellido': 'Sistema', 'rol': 0},
    {'username': 'supervisor1', 'nombre': 'Maria', 'apellido': 'Gonzalez', 'rol': 1},
    {'username': 'tecnico1', 'nombre': 'Pedro', 'apellido': 'Soto', 'rol': 2},
    {'username': 'tecnico2', 'nombre': 'Luis', 'apellido': 'Vargas', 'rol': 2},
    {'username': 'operador1', 'nombre': 'Andres', 'apellido': 'Torres', 'rol': 3},
    {'username': 'operador2', 'nombre': 'Felipe', 'apellido': 'Rojas', 'rol': 3},
]

usuarios = []
for data in usuarios_data:
    user, created = User.objects.get_or_create(
        username=data['username'],
        defaults={
            'first_name': data['nombre'],
            'last_name': data['apellido'],
            'is_staff': data['rol'] == 0,
            'is_active': True
        }
    )
    if created:
        user.set_password('somacor2024')
        user.save()
    
    usuario, _ = Usuarios.objects.get_or_create(
        user=user,
        defaults={'idrol': roles[data['rol']]}
    )
    usuarios.append(usuario)
print(f"   OK - {len(usuarios)} usuarios creados\n")

# RESUMEN
print("="*80)
print("RESUMEN")
print("="*80)
print(f"Tipos de Equipo: {len(tipos)}")
for tipo in tipos:
    count = Equipos.objects.filter(idtipoequipo=tipo).count()
    print(f"  - {tipo.nombretipo}: {count} equipos")
print(f"\nFaenas: {len(faenas)}")
print(f"Equipos: {len(equipos)}")
print(f"Usuarios: {len(usuarios)}")
print("\nCredenciales:")
print("  Usuario: admin")
print("  Password: somacor2024")
print("="*80)
print("COMPLETADO\n")
