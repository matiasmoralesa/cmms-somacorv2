#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de instalación de dependencias para el sistema CMMS
Verifica e instala todas las dependencias necesarias
"""

import os
import sys
import subprocess
from pathlib import Path

# Colores para la consola
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Imprime un encabezado formateado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_success(message: str):
    """Imprime un mensaje de éxito"""
    print(f"{Colors.GREEN}[OK] {message}{Colors.END}")

def print_error(message: str):
    """Imprime un mensaje de error"""
    print(f"{Colors.RED}[ERROR] {message}{Colors.END}")

def print_warning(message: str):
    """Imprime un mensaje de advertencia"""
    print(f"{Colors.YELLOW}[WARN] {message}{Colors.END}")

def print_info(message: str):
    """Imprime información"""
    print(f"{Colors.BLUE}[*] {message}{Colors.END}")

def check_python_version():
    """Verifica la versión de Python"""
    print_info("Verificando version de Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detectado")
        return True
    else:
        print_error(f"Se requiere Python 3.8 o superior. Version actual: {version.major}.{version.minor}")
        return False

def check_pip():
    """Verifica que pip esté instalado"""
    print_info("Verificando pip...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      capture_output=True, check=True)
        print_success("pip esta instalado")
        return True
    except subprocess.CalledProcessError:
        print_error("pip no esta instalado")
        return False

def install_package(package: str):
    """Instala un paquete usando pip"""
    try:
        print_info(f"Instalando {package}...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', package, '--upgrade'], 
                      check=True, capture_output=True)
        print_success(f"{package} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Error instalando {package}: {e}")
        return False

def check_package(package: str):
    """Verifica si un paquete está instalado"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def install_dependencies():
    """Instala todas las dependencias necesarias"""
    print_header("INSTALACION DE DEPENDENCIAS")
    
    # Dependencias requeridas
    dependencies = [
        ('requests', 'requests'),
        ('django', 'Django'),
        ('djangorestframework', 'djangorestframework'),
        ('django-cors-headers', 'django-cors-headers'),
        ('django-filter', 'django-filter'),
        ('channels', 'channels'),
        ('channels-redis', 'channels-redis'),
        ('Pillow', 'Pillow'),
        ('python-decouple', 'python-decouple'),
    ]
    
    print_info(f"Verificando {len(dependencies)} dependencias...")
    print()
    
    installed = 0
    failed = 0
    
    for package_name, import_name in dependencies:
        if check_package(import_name):
            print_success(f"{package_name} ya esta instalado")
            installed += 1
        else:
            print_warning(f"{package_name} no esta instalado")
            if install_package(package_name):
                installed += 1
            else:
                failed += 1
        print()
    
    print_header("RESUMEN DE INSTALACION")
    print(f"{Colors.GREEN}Instalados/Actualizados: {installed}{Colors.END}")
    if failed > 0:
        print(f"{Colors.RED}Fallidos: {failed}{Colors.END}")
    print()
    
    return failed == 0

def check_database():
    """Verifica la base de datos"""
    print_header("VERIFICACION DE BASE DE DATOS")
    
    db_file = Path(__file__).parent / 'db.sqlite3'
    
    if db_file.exists():
        print_success(f"Base de datos encontrada: {db_file}")
        size = db_file.stat().st_size / (1024 * 1024)  # MB
        print_info(f"Tamaño: {size:.2f} MB")
    else:
        print_warning("Base de datos no encontrada. Se creara al ejecutar migrate")
    
    print()

def check_migrations():
    """Verifica las migraciones"""
    print_header("VERIFICACION DE MIGRACIONES")
    
    print_info("Verificando migraciones pendientes...")
    
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'showmigrations', '--plan'],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Migraciones verificadas correctamente")
            
            # Contar migraciones aplicadas y pendientes
            output = result.stdout
            applied = output.count('[X]')
            pending = output.count('[ ]')
            
            print_info(f"Migraciones aplicadas: {applied}")
            print_info(f"Migraciones pendientes: {pending}")
            
            if pending > 0:
                print_warning(f"Hay {pending} migraciones pendientes")
                print_info("Ejecuta: python manage.py migrate")
        else:
            print_error("Error verificando migraciones")
            print_error(result.stderr)
    except Exception as e:
        print_error(f"Error: {e}")
    
    print()

def create_env_file():
    """Crea el archivo .env si no existe"""
    print_header("VERIFICACION DE ARCHIVO .ENV")
    
    env_file = Path(__file__).parent / '.env'
    
    if env_file.exists():
        print_success("Archivo .env encontrado")
    else:
        print_warning("Archivo .env no encontrado")
        print_info("Creando archivo .env con valores por defecto...")
        
        env_content = """# Configuración de Django
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=django-insecure-*c#pae09w^*q52ne6qz569qanvama$m%5yi)h$-7cj4&(5ydv%

# Configuración de base de datos
USE_MYSQL=False
DB_NAME=cmms_db
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

# Configuración de bot
BOT_WEBHOOK_URL=http://localhost:5000/webhook
"""
        
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            print_success("Archivo .env creado correctamente")
        except Exception as e:
            print_error(f"Error creando archivo .env: {e}")
    
    print()

def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("="*80)
    print("          INSTALACION Y VERIFICACION DE DEPENDENCIAS".center(80))
    print("                        Sistema CMMS Somacor".center(80))
    print("="*80)
    print(f"{Colors.END}\n")
    
    # Verificaciones
    if not check_python_version():
        print_error("Por favor, instala Python 3.8 o superior")
        sys.exit(1)
    
    if not check_pip():
        print_error("Por favor, instala pip")
        sys.exit(1)
    
    print()
    
    # Instalación de dependencias
    if not install_dependencies():
        print_error("Algunas dependencias no se pudieron instalar")
        print_warning("Puedes intentar instalarlas manualmente")
        sys.exit(1)
    
    # Verificaciones adicionales
    check_database()
    check_migrations()
    create_env_file()
    
    print_header("INSTALACION COMPLETADA")
    print_success("Todas las dependencias estan instaladas correctamente")
    print()
    print_info("Siguiente paso: Ejecuta las migraciones")
    print_info("Comando: python manage.py migrate")
    print()
    print_info("Luego inicia el servidor")
    print_info("Comando: python manage.py runserver")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[WARN] Instalacion interrumpida{Colors.END}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}[ERROR] Error inesperado: {str(e)}{Colors.END}\n")
        sys.exit(1)

