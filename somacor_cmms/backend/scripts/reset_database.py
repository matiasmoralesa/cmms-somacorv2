"""
Script maestro para resetear y poblar la base de datos con datos realistas
Ejecuta todos los scripts necesarios en orden
"""

import os
import sys
import subprocess

# Colores
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


def ejecutar_script(script_path, descripcion):
    """Ejecutar un script Python"""
    print_info(f"Ejecutando: {descripcion}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Mostrar output
        if result.stdout:
            print(result.stdout)
        
        print_success(f"Completado: {descripcion}\n")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Error en: {descripcion}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def confirmar_reset():
    """Pedir confirmación antes de resetear"""
    print_header("⚠️  ADVERTENCIA")
    print(f"{Colors.YELLOW}Este script eliminará TODOS los datos de la base de datos{Colors.END}")
    print(f"{Colors.YELLOW}y los reemplazará con datos realistas del año 2024.{Colors.END}\n")
    
    respuesta = input(f"{Colors.BOLD}¿Deseas continuar? (si/no): {Colors.END}").lower()
    
    return respuesta in ['si', 's', 'yes', 'y']


def main():
    """Función principal"""
    print_header("RESET COMPLETO DE BASE DE DATOS")
    print(f"{Colors.BOLD}Sistema CMMS Somacor{Colors.END}")
    print(f"{Colors.BOLD}Datos Realistas 2024{Colors.END}\n")
    
    # Confirmar
    if not confirmar_reset():
        print_info("Operación cancelada por el usuario")
        return
    
    print_header("INICIANDO PROCESO")
    
    # Directorio de scripts
    scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
    
    # Scripts a ejecutar en orden
    scripts = [
        {
            'path': os.path.join(scripts_dir, 'reset_and_populate_realistic.py'),
            'descripcion': 'Limpiar BD y crear datos base (equipos, usuarios, faenas)'
        },
        {
            'path': os.path.join(scripts_dir, 'generate_year_data.py'),
            'descripcion': 'Generar datos históricos del año 2024'
        }
    ]
    
    # Ejecutar scripts
    exitos = 0
    for script in scripts:
        if os.path.exists(script['path']):
            if ejecutar_script(script['path'], script['descripcion']):
                exitos += 1
        else:
            print_warning(f"Script no encontrado: {script['path']}")
    
    # Resumen final
    print_header("RESUMEN FINAL")
    
    if exitos == len(scripts):
        print_success(f"Todos los scripts ejecutados exitosamente ({exitos}/{len(scripts)})")
        
        print(f"\n{Colors.BOLD}🎉 BASE DE DATOS LISTA{Colors.END}\n")
        print(f"{Colors.BOLD}Datos generados:{Colors.END}")
        print(f"   • 5 tipos de equipos")
        print(f"   • 20 equipos distribuidos en 3 faenas")
        print(f"   • 13 usuarios (admin, supervisores, técnicos, operadores)")
        print(f"   • Datos históricos del año 2024")
        print(f"   • Checklists diarios (~4,700)")
        print(f"   • Órdenes de trabajo (~720)")
        
        print(f"\n{Colors.BOLD}🔑 Credenciales de acceso:{Colors.END}")
        print(f"   • Usuario: admin.santiago")
        print(f"   • Password: somacor2024")
        
        print(f"\n{Colors.BOLD}🚀 Próximos pasos:{Colors.END}")
        print(f"   1. Iniciar el backend: python manage.py runserver")
        print(f"   2. Acceder al sistema con las credenciales")
        print(f"   3. Explorar los datos generados")
        
    else:
        print_error(f"Algunos scripts fallaron ({exitos}/{len(scripts)})")
        print_warning("Revisa los errores anteriores")
    
    print()


if __name__ == '__main__':
    main()
