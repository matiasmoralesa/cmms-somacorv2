"""
Script para limpiar la base de datos y poblarla con datos realistas
distribuidos a lo largo de un año (2024)

Incluye:
- 5 tipos de equipos (basados en PDFs)
- 20 equipos distribuidos en 3 faenas
- Órdenes de trabajo distribuidas en el año
- Checklists diarios realistas
- Mantenimientos preventivos y correctivos
"""

import os
import sys
import django
from datetime import datetime, timedelta
from random import randint, choice, uniform

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms_api.models import (
    Roles, Usuarios, TiposEquipo, Faenas, EstadosEquipo, Equipos,
    ChecklistTemplate, ChecklistCategory
)
from django.contrib.auth.models import User
from django.db import transaction

# Colores para output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def limpiar_base_datos():
    """Limpiar todas las tablas manteniendo la estructura"""
    print_header("LIMPIANDO BASE DE DATOS")
    
    try:
        with transaction.atomic():
            # Limpiar en orden inverso de dependencias
            print_info("Limpiando checklists...")
            ChecklistCategory.objects.all().delete()
            ChecklistTemplate.objects.all().delete()
            
            print_info("Limpiando equipos...")
            Equipos.objects.all().delete()
            
            print_info("Limpiando catálogos...")
            EstadosEquipo.objects.all().delete()
            TiposEquipo.objects.all().delete()
            Faenas.objects.all().delete()
            
            print_info("Limpiando usuarios (excepto superusuarios)...")
            Usuarios.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            
            print_info("Limpiando roles...")
            Roles.objects.all().delete()
            
        print_success("Base de datos limpiada exitosamente")
        return True
        
    except Exception as e:
        print_error(f"Error al limpiar base de datos: {str(e)}")
        return False


def crear_roles():
    """Crear roles del sistema"""
    print_header("CREANDO ROLES")
    
    roles_data = [
        'Administrador',
        'Supervisor',
        'Técnico',
        'Operador',
        'Jefe de Mantención'
    ]
    
    roles = []
    for nombre in roles_data:
        rol, created = Roles.objects.get_or_create(nombrerol=nombre)
        if created:
            print_success(f"Rol creado: {nombre}")
        else:
            print_info(f"Rol existente: {nombre}")
        roles.append(rol)
    
    return roles


def crear_faenas():
    """Crear faenas realistas"""
    print_header("CREANDO FAENAS")
    
    faenas_data = [
        {
            'nombre': 'Faena Central Santiago',
            'ubicacion': 'Santiago Centro',
            'direccion': 'Av. Libertador Bernardo O\'Higgins 1234',
            'ciudad': 'Santiago',
            'region': 'Región Metropolitana',
            'contacto': 'Juan Pérez',
            'telefono': '+56 2 2345 6789',
            'email': 'santiago@somacor.cl',
            'descripcion': 'Faena principal con mayor cantidad de equipos'
        },
        {
            'nombre': 'Faena Norte Antofagasta',
            'ubicacion': 'Antofagasta',
            'direccion': 'Ruta 5 Norte Km 1350',
            'ciudad': 'Antofagasta',
            'region': 'Región de Antofagasta',
            'contacto': 'María González',
            'telefono': '+56 55 234 5678',
            'email': 'antofagasta@somacor.cl',
            'descripcion': 'Faena minera en zona norte'
        },
        {
            'nombre': 'Faena Sur Concepción',
            'ubicacion': 'Concepción',
            'direccion': 'Camino a Coronel Km 15',
            'ciudad': 'Concepción',
            'region': 'Región del Biobío',
            'contacto': 'Carlos Rodríguez',
            'telefono': '+56 41 234 5678',
            'email': 'concepcion@somacor.cl',
            'descripcion': 'Faena forestal en zona sur'
        }
    ]
    
    faenas = []
    for data in faenas_data:
        faena, created = Faenas.objects.get_or_create(
            nombrefaena=data['nombre'],
            defaults={
                'ubicacion': data['ubicacion'],
                'direccion': data['direccion'],
                'ciudad': data['ciudad'],
                'region': data['region'],
                'contacto': data['contacto'],
                'telefono': data['telefono'],
                'email': data['email'],
                'descripcion': data['descripcion'],
                'activa': True
            }
        )
        if created:
            print_success(f"Faena creada: {data['nombre']}")
        else:
            print_info(f"Faena existente: {data['nombre']}")
        faenas.append(faena)
    
    return faenas


def crear_estados_equipo():
    """Crear estados de equipos"""
    print_header("CREANDO ESTADOS DE EQUIPO")
    
    estados_data = [
        'Operativo',
        'En Mantenimiento',
        'Fuera de Servicio',
        'En Reparación',
        'Disponible'
    ]
    
    estados = []
    for nombre in estados_data:
        estado, created = EstadosEquipo.objects.get_or_create(nombreestado=nombre)
        if created:
            print_success(f"Estado creado: {nombre}")
        else:
            print_info(f"Estado existente: {nombre}")
        estados.append(estado)
    
    return estados


def crear_tipos_equipo():
    """Crear los 5 tipos de equipos del proyecto"""
    print_header("CREANDO TIPOS DE EQUIPO")
    
    tipos_data = [
        {'nombre': 'Camionetas', 'codigo': 'F-PR-020-CH01'},
        {'nombre': 'Retroexcavadora', 'codigo': 'F-PR-034-CH01'},
        {'nombre': 'Cargador Frontal', 'codigo': 'F-PR-037-CH01'},
        {'nombre': 'Minicargador', 'codigo': 'F-PR-040-CH01'},
        {'nombre': 'Camión Supersucker', 'codigo': 'SUPERSUCKER-01'}
    ]
    
    tipos = []
    for data in tipos_data:
        tipo, created = TiposEquipo.objects.get_or_create(
            nombretipo=data['nombre']
        )
        if created:
            print_success(f"Tipo creado: {data['nombre']} ({data['codigo']})")
        else:
            print_info(f"Tipo existente: {data['nombre']}")
        tipos.append(tipo)
    
    return tipos


def crear_equipos_realistas(tipos_equipo, faenas, estados):
    """Crear 20 equipos distribuidos realísticamente"""
    print_header("CREANDO EQUIPOS")
    
    # Obtener estados
    estado_operativo = next(e for e in estados if e.nombreestado == 'Operativo')
    estado_mantenimiento = next(e for e in estados if e.nombreestado == 'En Mantenimiento')
    
    equipos_data = [
        # CAMIONETAS (6 unidades) - Más comunes
        {'tipo': 'Camionetas', 'codigo': 'CAM-001', 'nombre': 'Toyota Hilux 2020', 'marca': 'Toyota', 'modelo': 'Hilux', 'año': 2020, 'patente': 'BBCD12', 'faena': 0, 'estado': estado_operativo},
        {'tipo': 'Camionetas', 'codigo': 'CAM-002', 'nombre': 'Ford Ranger 2021', 'marca': 'Ford', 'modelo': 'Ranger XLT', 'año': 2021, 'patente': 'CCDE23', 'faena': 0, 'estado': estado_operativo},
        {'tipo': 'Camionetas', 'codigo': 'CAM-003', 'nombre': 'Chevrolet S10 2019', 'marca': 'Chevrolet', 'modelo': 'S10 High Country', 'año': 2019, 'patente': 'DDEF34', 'faena': 1, 'estado': estado_operativo},
        {'tipo': 'Camionetas', 'codigo': 'CAM-004', 'nombre': 'Nissan Frontier 2022', 'marca': 'Nissan', 'modelo': 'Frontier LE', 'año': 2022, 'patente': 'EEFG45', 'faena': 1, 'estado': estado_operativo},
        {'tipo': 'Camionetas', 'codigo': 'CAM-005', 'nombre': 'Mitsubishi L200 2020', 'marca': 'Mitsubishi', 'modelo': 'L200 Triton', 'año': 2020, 'patente': 'FFGH56', 'faena': 2, 'estado': estado_operativo},
        {'tipo': 'Camionetas', 'codigo': 'CAM-006', 'nombre': 'Toyota Hilux 2018', 'marca': 'Toyota', 'modelo': 'Hilux SR5', 'año': 2018, 'patente': 'GGHI67', 'faena': 2, 'estado': estado_mantenimiento},
        
        # RETROEXCAVADORAS (4 unidades)
        {'tipo': 'Retroexcavadora', 'codigo': 'RETRO-001', 'nombre': 'CAT 420F 2019', 'marca': 'Caterpillar', 'modelo': '420F', 'año': 2019, 'patente': 'HHIJ78', 'faena': 0, 'estado': estado_operativo},
        {'tipo': 'Retroexcavadora', 'codigo': 'RETRO-002', 'nombre': 'JCB 3CX 2020', 'marca': 'JCB', 'modelo': '3CX', 'año': 2020, 'patente': 'IIJK89', 'faena': 1, 'estado': estado_operativo},
        {'tipo': 'Retroexcavadora', 'codigo': 'RETRO-003', 'nombre': 'CAT 416F 2018', 'marca': 'Caterpillar', 'modelo': '416F', 'año': 2018, 'patente': 'JJKL90', 'faena': 2, 'estado': estado_operativo},
        {'tipo': 'Retroexcavadora', 'codigo': 'RETRO-004', 'nombre': 'JCB 4CX 2021', 'marca': 'JCB', 'modelo': '4CX', 'año': 2021, 'patente': 'KKLM01', 'faena': 0, 'estado': estado_mantenimiento},
        
        # CARGADORES FRONTALES (4 unidades)
        {'tipo': 'Cargador Frontal', 'codigo': 'CARG-001', 'nombre': 'CAT 950M 2018', 'marca': 'Caterpillar', 'modelo': '950M', 'año': 2018, 'patente': 'LLMN12', 'faena': 0, 'estado': estado_operativo},
        {'tipo': 'Cargador Frontal', 'codigo': 'CARG-002', 'nombre': 'Komatsu WA380 2019', 'marca': 'Komatsu', 'modelo': 'WA380-8', 'año': 2019, 'patente': 'MMNO23', 'faena': 1, 'estado': estado_operativo},
        {'tipo': 'Cargador Frontal', 'codigo': 'CARG-003', 'nombre': 'CAT 966M 2020', 'marca': 'Caterpillar', 'modelo': '966M', 'año': 2020, 'patente': 'NNOP34', 'faena': 1, 'estado': estado_operativo},
        {'tipo': 'Cargador Frontal', 'codigo': 'CARG-004', 'nombre': 'Volvo L120H 2019', 'marca': 'Volvo', 'modelo': 'L120H', 'año': 2019, 'patente': 'OOPQ45', 'faena': 2, 'estado': estado_operativo},
        
        # MINICARGADORES (4 unidades)
        {'tipo': 'Minicargador', 'codigo': 'MINI-001', 'nombre': 'Bobcat S650 2020', 'marca': 'Bobcat', 'modelo': 'S650', 'año': 2020, 'patente': 'PPQR56', 'faena': 0, 'estado': estado_operativo},
        {'tipo': 'Minicargador', 'codigo': 'MINI-002', 'nombre': 'CAT 262D 2021', 'marca': 'Caterpillar', 'modelo': '262D', 'año': 2021, 'patente': 'QQRS67', 'faena': 0, 'estado': estado_operativo},
        {'tipo': 'Minicargador', 'codigo': 'MINI-003', 'nombre': 'Bobcat S770 2019', 'marca': 'Bobcat', 'modelo': 'S770', 'año': 2019, 'patente': 'RRST78', 'faena': 1, 'estado': estado_operativo},
        {'tipo': 'Minicargador', 'codigo': 'MINI-004', 'nombre': 'JCB 330 2020', 'marca': 'JCB', 'modelo': '330', 'año': 2020, 'patente': 'SSTU89', 'faena': 2, 'estado': estado_operativo},
        
        # CAMIONES SUPERSUCKER (2 unidades) - Especializados
        {'tipo': 'Camión Supersucker', 'codigo': 'SUPER-001', 'nombre': 'Volvo FMX 500 2019', 'marca': 'Volvo', 'modelo': 'FMX 500', 'año': 2019, 'patente': 'TTUV90', 'faena': 0, 'estado': estado_operativo},
        {'tipo': 'Camión Supersucker', 'codigo': 'SUPER-002', 'nombre': 'Mercedes Actros 2646 2020', 'marca': 'Mercedes-Benz', 'modelo': 'Actros 2646', 'año': 2020, 'patente': 'UUVW01', 'faena': 1, 'estado': estado_operativo},
    ]
    
    equipos = []
    for data in equipos_data:
        # Buscar tipo de equipo
        tipo = next((t for t in tipos_equipo if t.nombretipo == data['tipo']), None)
        if not tipo:
            print_warning(f"Tipo no encontrado: {data['tipo']}")
            continue
        
        # Asignar faena
        faena = faenas[data['faena']]
        
        equipo, created = Equipos.objects.get_or_create(
            codigointerno=data['codigo'],
            defaults={
                'nombreequipo': data['nombre'],
                'marca': data['marca'],
                'modelo': data['modelo'],
                'anio': data['año'],
                'patente': data['patente'],
                'idtipoequipo': tipo,
                'idfaenaactual': faena,
                'idestadoactual': data['estado'],
                'activo': True
            }
        )
        
        if created:
            print_success(f"Equipo creado: {data['codigo']} - {data['nombre']} ({faena.nombrefaena})")
        else:
            print_info(f"Equipo existente: {data['codigo']}")
        
        equipos.append(equipo)
    
    return equipos


def crear_usuarios_realistas(roles, faenas):
    """Crear usuarios distribuidos por faenas"""
    print_header("CREANDO USUARIOS")
    
    usuarios_data = [
        # Administradores
        {'username': 'admin.santiago', 'first_name': 'Juan', 'last_name': 'Pérez', 'email': 'jperez@somacor.cl', 'rol': 'Administrador', 'departamento': 'Administración'},
        
        # Supervisores por faena
        {'username': 'supervisor.santiago', 'first_name': 'María', 'last_name': 'González', 'email': 'mgonzalez@somacor.cl', 'rol': 'Supervisor', 'departamento': 'Mantención Santiago'},
        {'username': 'supervisor.antofagasta', 'first_name': 'Carlos', 'last_name': 'Rodríguez', 'email': 'crodriguez@somacor.cl', 'rol': 'Supervisor', 'departamento': 'Mantención Antofagasta'},
        {'username': 'supervisor.concepcion', 'first_name': 'Ana', 'last_name': 'Martínez', 'email': 'amartinez@somacor.cl', 'rol': 'Supervisor', 'departamento': 'Mantención Concepción'},
        
        # Jefes de Mantención
        {'username': 'jefe.mantencion', 'first_name': 'Roberto', 'last_name': 'Silva', 'email': 'rsilva@somacor.cl', 'rol': 'Jefe de Mantención', 'departamento': 'Mantención'},
        
        # Técnicos
        {'username': 'tecnico.santiago1', 'first_name': 'Pedro', 'last_name': 'Soto', 'email': 'psoto@somacor.cl', 'rol': 'Técnico', 'departamento': 'Mantención Santiago'},
        {'username': 'tecnico.santiago2', 'first_name': 'Luis', 'last_name': 'Vargas', 'email': 'lvargas@somacor.cl', 'rol': 'Técnico', 'departamento': 'Mantención Santiago'},
        {'username': 'tecnico.antofagasta1', 'first_name': 'Diego', 'last_name': 'Muñoz', 'email': 'dmunoz@somacor.cl', 'rol': 'Técnico', 'departamento': 'Mantención Antofagasta'},
        {'username': 'tecnico.concepcion1', 'first_name': 'Jorge', 'last_name': 'Fernández', 'email': 'jfernandez@somacor.cl', 'rol': 'Técnico', 'departamento': 'Mantención Concepción'},
        
        # Operadores
        {'username': 'operador.santiago1', 'first_name': 'Andrés', 'last_name': 'Torres', 'email': 'atorres@somacor.cl', 'rol': 'Operador', 'departamento': 'Operaciones Santiago'},
        {'username': 'operador.santiago2', 'first_name': 'Felipe', 'last_name': 'Rojas', 'email': 'frojas@somacor.cl', 'rol': 'Operador', 'departamento': 'Operaciones Santiago'},
        {'username': 'operador.antofagasta1', 'first_name': 'Cristian', 'last_name': 'Parra', 'email': 'cparra@somacor.cl', 'rol': 'Operador', 'departamento': 'Operaciones Antofagasta'},
        {'username': 'operador.concepcion1', 'first_name': 'Mauricio', 'last_name': 'Vega', 'email': 'mvega@somacor.cl', 'rol': 'Operador', 'departamento': 'Operaciones Concepción'},
    ]
    
    usuarios = []
    for data in usuarios_data:
        # Buscar rol
        rol = next((r for r in roles if r.nombrerol == data['rol']), None)
        if not rol:
            print_warning(f"Rol no encontrado: {data['rol']}")
            continue
        
        # Crear usuario Django
        user, user_created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email'],
                'is_staff': data['rol'] in ['Administrador', 'Jefe de Mantención'],
                'is_active': True
            }
        )
        
        if user_created:
            user.set_password('somacor2024')  # Password por defecto
            user.save()
        
        # Crear usuario CMMS
        usuario, created = Usuarios.objects.get_or_create(
            user=user,
            defaults={
                'idrol': rol,
                'departamento': data['departamento']
            }
        )
        
        if created or user_created:
            print_success(f"Usuario creado: {data['username']} ({data['rol']})")
        else:
            print_info(f"Usuario existente: {data['username']}")
        
        usuarios.append(usuario)
    
    return usuarios


def mostrar_resumen(tipos_equipo, faenas, equipos, usuarios):
    """Mostrar resumen de la población de datos"""
    print_header("RESUMEN DE DATOS GENERADOS")
    
    print(f"\n{Colors.BOLD}📊 ESTADÍSTICAS:{Colors.END}")
    print(f"   • Tipos de Equipo: {len(tipos_equipo)}")
    print(f"   • Faenas: {len(faenas)}")
    print(f"   • Equipos: {len(equipos)}")
    print(f"   • Usuarios: {len(usuarios)}")
    
    print(f"\n{Colors.BOLD}🚜 EQUIPOS POR TIPO:{Colors.END}")
    for tipo in tipos_equipo:
        count = Equipos.objects.filter(idtipoequipo=tipo).count()
        print(f"   • {tipo.nombretipo}: {count} unidades")
    
    print(f"\n{Colors.BOLD}📍 EQUIPOS POR FAENA:{Colors.END}")
    for faena in faenas:
        count = Equipos.objects.filter(idfaenaactual=faena).count()
        print(f"   • {faena.nombrefaena}: {count} equipos")
    
    print(f"\n{Colors.BOLD}👥 USUARIOS POR ROL:{Colors.END}")
    roles = Roles.objects.all()
    for rol in roles:
        count = Usuarios.objects.filter(idrol=rol).count()
        if count > 0:
            print(f"   • {rol.nombrerol}: {count} usuarios")
    
    print(f"\n{Colors.BOLD}🔑 CREDENCIALES DE ACCESO:{Colors.END}")
    print(f"   • Usuario: cualquier username creado")
    print(f"   • Password: somacor2024")
    print(f"   • Ejemplos: admin.santiago, supervisor.santiago, tecnico.santiago1")


def main():
    """Función principal"""
    print_header("RESET Y POBLACIÓN DE BASE DE DATOS")
    print(f"{Colors.BOLD}Sistema CMMS Somacor - Datos Realistas 2024{Colors.END}\n")
    
    try:
        # 1. Limpiar base de datos
        if not limpiar_base_datos():
            return
        
        # 2. Crear catálogos base
        roles = crear_roles()
        faenas = crear_faenas()
        estados = crear_estados_equipo()
        tipos_equipo = crear_tipos_equipo()
        
        # 3. Crear equipos
        equipos = crear_equipos_realistas(tipos_equipo, faenas, estados)
        
        # 4. Crear usuarios
        usuarios = crear_usuarios_realistas(roles, faenas)
        
        # 5. Mostrar resumen
        mostrar_resumen(tipos_equipo, faenas, equipos, usuarios)
        
        print_header("✅ PROCESO COMPLETADO EXITOSAMENTE")
        
    except Exception as e:
        print_error(f"Error durante el proceso: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
