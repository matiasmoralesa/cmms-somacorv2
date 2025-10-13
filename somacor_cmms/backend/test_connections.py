#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de verificación completa de conexiones Frontend-Backend
Verifica que todos los endpoints estén funcionando correctamente
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Configurar encoding para Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"
API_V2 = f"{API_BASE}/v2"

# Colores para la consola
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Contadores de resultados
results = {
    'passed': 0,
    'failed': 0,
    'warnings': 0,
    'total': 0
}

def print_header(text: str):
    """Imprime un encabezado formateado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_test(test_name: str):
    """Imprime el nombre de una prueba"""
    print(f"{Colors.BLUE}[*] {test_name}...{Colors.END}", end=" ")

def print_success(message: str = "[OK]"):
    """Imprime un mensaje de éxito"""
    print(f"{Colors.GREEN}{message}{Colors.END}")
    results['passed'] += 1

def print_failure(message: str):
    """Imprime un mensaje de error"""
    print(f"{Colors.RED}[FAIL] {message}{Colors.END}")
    results['failed'] += 1

def print_warning(message: str):
    """Imprime un mensaje de advertencia"""
    print(f"{Colors.YELLOW}[WARN] {message}{Colors.END}")
    results['warnings'] += 1

def print_info(message: str):
    """Imprime información"""
    print(f"  {Colors.CYAN}{message}{Colors.END}")

def test_connection():
    """Prueba la conexión básica al servidor"""
    print_header("VERIFICACIÓN DE CONEXIÓN BÁSICA")
    
    print_test("Conexión al servidor Django")
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print_success()
            return True
        else:
            print_failure(f"Código de estado: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_failure("No se puede conectar al servidor. ¿Está corriendo en http://localhost:8000?")
        return False
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        return False

def test_api_endpoints():
    """Prueba los endpoints de la API"""
    print_header("VERIFICACIÓN DE ENDPOINTS DE LA API")
    
    endpoints = [
        # Endpoints básicos
        ("API Root", f"{API_BASE}/"),
        ("Faenas", f"{API_BASE}/faenas/"),
        ("Tipos de Equipo", f"{API_BASE}/tipos-equipo/"),
        ("Estados de Equipo", f"{API_BASE}/estados-equipo/"),
        ("Roles", f"{API_BASE}/roles/"),
        
        # Endpoints V2
        ("Equipos V2", f"{API_V2}/equipos/"),
        ("Órdenes de Trabajo V2", f"{API_V2}/ordenes-trabajo/"),
        ("Dashboard Stats V2", f"{API_V2}/dashboard/stats/"),
        ("Dashboard Monthly Data V2", f"{API_V2}/dashboard/monthly_data/"),
        ("Dashboard Maintenance Types V2", f"{API_V2}/dashboard/maintenance_types/"),
        ("Usuarios V2", f"{API_V2}/usuarios/"),
        ("Faenas V2", f"{API_V2}/faenas/"),
        ("Tipos de Equipo V2", f"{API_V2}/tipos-equipo/"),
    ]
    
    for name, url in endpoints:
        print_test(name)
        try:
            response = requests.get(url, timeout=10)
            results['total'] += 1
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    count = len(data['results'])
                    print_success(f"✓ OK ({count} items)")
                elif isinstance(data, list):
                    print_success(f"✓ OK ({len(data)} items)")
                else:
                    print_success()
            elif response.status_code == 401:
                print_warning("Requiere autenticación (esperado)")
            elif response.status_code == 404:
                print_failure("Endpoint no encontrado")
            else:
                print_failure(f"Código: {response.status_code}")
        except requests.exceptions.Timeout:
            print_failure("Timeout")
        except Exception as e:
            print_failure(f"Error: {str(e)}")

def test_cors_configuration():
    """Verifica la configuración de CORS"""
    print_header("VERIFICACIÓN DE CONFIGURACIÓN CORS")
    
    print_test("CORS Headers")
    try:
        response = requests.options(
            f"{API_BASE}/faenas/",
            headers={
                'Origin': 'http://localhost:5173',
                'Access-Control-Request-Method': 'GET'
            },
            timeout=5
        )
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        if cors_headers['Access-Control-Allow-Origin']:
            print_success()
            print_info(f"Origen permitido: {cors_headers['Access-Control-Allow-Origin']}")
            print_info(f"Métodos permitidos: {cors_headers['Access-Control-Allow-Methods']}")
        else:
            print_warning("CORS no configurado correctamente")
    except Exception as e:
        print_failure(f"Error: {str(e)}")

def test_data_consistency():
    """Verifica la consistencia de los datos"""
    print_header("VERIFICACIÓN DE CONSISTENCIA DE DATOS")
    
    # Verificar que los datos básicos existan
    tests = [
        ("Faenas", f"{API_BASE}/faenas/"),
        ("Tipos de Equipo", f"{API_BASE}/tipos-equipo/"),
        ("Estados de Equipo", f"{API_BASE}/estados-equipo/"),
        ("Roles", f"{API_BASE}/roles/"),
    ]
    
    for name, url in tests:
        print_test(f"Datos de {name}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    if len(data['results']) > 0:
                        print_success(f"✓ OK ({len(data['results'])} registros)")
                    else:
                        print_warning(f"No hay datos de {name}")
                else:
                    print_warning(f"Formato de respuesta inesperado")
            else:
                print_failure(f"Código: {response.status_code}")
        except Exception as e:
            print_failure(f"Error: {str(e)}")

def test_form_data_endpoints():
    """Verifica los endpoints necesarios para los formularios"""
    print_header("VERIFICACIÓN DE ENDPOINTS DE FORMULARIOS")
    
    # Endpoints necesarios para formularios
    form_endpoints = [
        ("Faenas para formularios", f"{API_V2}/faenas/"),
        ("Usuarios/Técnicos para formularios", f"{API_V2}/usuarios/"),
        ("Tipos de Equipo para formularios", f"{API_V2}/tipos-equipo/"),
        ("Estados de Equipo", f"{API_BASE}/estados-equipo/"),
        ("Roles", f"{API_V2}/roles/"),
    ]
    
    for name, url in form_endpoints:
        print_test(name)
        try:
            response = requests.get(url, timeout=10)
            results['total'] += 1
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    count = len(data['results'])
                    print_success(f"✓ OK ({count} items)")
                elif isinstance(data, list):
                    print_success(f"✓ OK ({len(data)} items)")
                else:
                    print_success()
            else:
                print_failure(f"Código: {response.status_code}")
        except Exception as e:
            print_failure(f"Error: {str(e)}")

def test_search_functionality():
    """Verifica la funcionalidad de búsqueda"""
    print_header("VERIFICACIÓN DE FUNCIONALIDAD DE BÚSQUEDA")
    
    search_tests = [
        ("Búsqueda de Equipos", f"{API_V2}/search/equipos/?search=test"),
        ("Búsqueda de Órdenes", f"{API_V2}/search/ordenes/?search=test"),
    ]
    
    for name, url in search_tests:
        print_test(name)
        try:
            response = requests.get(url, timeout=10)
            results['total'] += 1
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    print_success(f"✓ OK ({len(data['results'])} resultados)")
                else:
                    print_success()
            else:
                print_failure(f"Código: {response.status_code}")
        except Exception as e:
            print_failure(f"Error: {str(e)}")

def test_dashboard_endpoints():
    """Verifica los endpoints del dashboard"""
    print_header("VERIFICACIÓN DE ENDPOINTS DEL DASHBOARD")
    
    dashboard_endpoints = [
        ("Dashboard Stats", f"{API_V2}/dashboard/stats/"),
        ("Dashboard Monthly Data", f"{API_V2}/dashboard/monthly_data/"),
        ("Dashboard Maintenance Types", f"{API_V2}/dashboard/maintenance_types/"),
    ]
    
    for name, url in dashboard_endpoints:
        print_test(name)
        try:
            response = requests.get(url, timeout=10)
            results['total'] += 1
            
            if response.status_code == 200:
                data = response.json()
                print_success()
                if isinstance(data, dict):
                    print_info(f"  Claves: {', '.join(data.keys())}")
            else:
                print_failure(f"Código: {response.status_code}")
        except Exception as e:
            print_failure(f"Error: {str(e)}")

def test_frontend_connectivity():
    """Verifica que el frontend pueda conectarse"""
    print_header("VERIFICACIÓN DE CONECTIVIDAD DEL FRONTEND")
    
    print_test("Frontend corriendo en puerto 5173")
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print_success()
        else:
            print_warning(f"Frontend responde con código: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print_warning("Frontend no está corriendo en http://localhost:5173")
    except Exception as e:
        print_warning(f"Error: {str(e)}")

def generate_report():
    """Genera un reporte final"""
    print_header("REPORTE FINAL")
    
    total_tests = results['passed'] + results['failed']
    success_rate = (results['passed'] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{Colors.BOLD}Resumen de Pruebas:{Colors.END}")
    print(f"  {Colors.GREEN}[OK] Exitosas: {results['passed']}{Colors.END}")
    print(f"  {Colors.RED}[FAIL] Fallidas: {results['failed']}{Colors.END}")
    print(f"  {Colors.YELLOW}[WARN] Advertencias: {results['warnings']}{Colors.END}")
    print(f"  Total: {total_tests}")
    print(f"\n{Colors.BOLD}Tasa de éxito: {success_rate:.1f}%{Colors.END}")
    
    if results['failed'] == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[OK] Todas las pruebas pasaron exitosamente!{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}[FAIL] Algunas pruebas fallaron. Revisa los errores arriba.{Colors.END}")
    
    print(f"\n{Colors.CYAN}Fecha de verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")

def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("="*80)
    print("          VERIFICACION COMPLETA DE CONEXIONES FRONTEND-BACKEND".center(80))
    print("                        Sistema CMMS Somacor".center(80))
    print("="*80)
    print(f"{Colors.END}\n")
    
    # Ejecutar todas las pruebas
    if not test_connection():
        print(f"\n{Colors.RED}{Colors.BOLD}[FAIL] No se pudo conectar al servidor. Por favor, inicia el servidor primero.{Colors.END}")
        print(f"{Colors.YELLOW}Ejecuta: python manage.py runserver{Colors.END}\n")
        sys.exit(1)
    
    test_api_endpoints()
    test_cors_configuration()
    test_data_consistency()
    test_form_data_endpoints()
    test_search_functionality()
    test_dashboard_endpoints()
    test_frontend_connectivity()
    
    # Generar reporte final
    generate_report()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Verificación interrumpida por el usuario.{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}Error inesperado: {str(e)}{Colors.END}\n")
        sys.exit(1)

