#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que los datos de formularios se carguen correctamente
"""

import requests
import json
import sys
import os

# Configurar encoding para Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"
API_V2 = f"{API_BASE}/v2"

# Colores
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_test(test_name: str):
    print(f"{Colors.BLUE}[*] {test_name}...{Colors.END}", end=" ")

def print_success(message: str = "[OK]"):
    print(f"{Colors.GREEN}{message}{Colors.END}")

def print_failure(message: str):
    print(f"{Colors.RED}[FAIL] {message}{Colors.END}")

def print_info(message: str):
    print(f"  {Colors.CYAN}{message}{Colors.END}")

def test_faenas():
    """Prueba endpoint de faenas"""
    print_test("Faenas")
    try:
        response = requests.get(f"{API_V2}/faenas/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                count = len(data['results'])
                print_success(f"[OK] ({count} faenas)")
                if count > 0:
                    print_info(f"Ejemplo: {data['results'][0].get('nombrefaena', 'N/A')}")
                return True
            else:
                print_failure("Formato de respuesta incorrecto")
                return False
        else:
            print_failure(f"Codigo: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        return False

def test_tipos_equipo():
    """Prueba endpoint de tipos de equipo"""
    print_test("Tipos de Equipo")
    try:
        response = requests.get(f"{API_V2}/tipos-equipo/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                count = len(data['results'])
                print_success(f"[OK] ({count} tipos)")
                if count > 0:
                    print_info(f"Ejemplo: {data['results'][0].get('nombretipo', 'N/A')}")
                return True
            else:
                print_failure("Formato de respuesta incorrecto")
                return False
        else:
            print_failure(f"Codigo: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        return False

def test_estados_equipo():
    """Prueba endpoint de estados de equipo"""
    print_test("Estados de Equipo")
    try:
        response = requests.get(f"{API_BASE}/estados-equipo/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                count = len(data['results'])
                print_success(f"[OK] ({count} estados)")
                if count > 0:
                    print_info(f"Ejemplo: {data['results'][0].get('nombreestado', 'N/A')}")
                return True
            else:
                print_failure("Formato de respuesta incorrecto")
                return False
        else:
            print_failure(f"Codigo: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        return False

def test_equipos():
    """Prueba endpoint de equipos"""
    print_test("Equipos")
    try:
        response = requests.get(f"{API_V2}/equipos/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                count = len(data['results'])
                print_success(f"[OK] ({count} equipos)")
                if count > 0:
                    equipo = data['results'][0]
                    print_info(f"Ejemplo: {equipo.get('nombreequipo', 'N/A')} ({equipo.get('codigointerno', 'N/A')})")
                return True
            else:
                print_failure("Formato de respuesta incorrecto")
                return False
        else:
            print_failure(f"Codigo: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        return False

def test_tipos_mantenimiento():
    """Prueba endpoint de tipos de mantenimiento"""
    print_test("Tipos de Mantenimiento")
    try:
        response = requests.get(f"{API_BASE}/tipos-mantenimiento-ot/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                count = len(data['results'])
                print_success(f"[OK] ({count} tipos)")
                if count > 0:
                    print_info(f"Ejemplo: {data['results'][0].get('nombretipo', 'N/A')}")
                return True
            else:
                print_failure("Formato de respuesta incorrecto")
                return False
        else:
            print_failure(f"Codigo: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        return False

def test_usuarios():
    """Prueba endpoint de usuarios"""
    print_test("Usuarios")
    try:
        response = requests.get(f"{API_V2}/usuarios/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                count = len(data['results'])
                print_success(f"[OK] ({count} usuarios)")
                if count > 0:
                    usuario = data['results'][0]
                    print_info(f"Ejemplo: {usuario.get('nombres', 'N/A')} {usuario.get('apellidos', 'N/A')}")
                return True
            else:
                print_failure("Formato de respuesta incorrecto")
                return False
        else:
            print_failure(f"Codigo: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        return False

def test_roles():
    """Prueba endpoint de roles"""
    print_test("Roles")
    try:
        response = requests.get(f"{API_V2}/roles/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                count = len(data['results'])
                print_success(f"[OK] ({count} roles)")
                if count > 0:
                    print_info(f"Ejemplo: {data['results'][0].get('nombrerol', 'N/A')}")
                return True
            else:
                print_failure("Formato de respuesta incorrecto")
                return False
        else:
            print_failure(f"Codigo: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        return False

def main():
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("="*80)
    print("          PRUEBA DE DATOS PARA FORMULARIOS".center(80))
    print("                        Sistema CMMS Somacor".center(80))
    print("="*80)
    print(f"{Colors.END}\n")

    results = []
    
    print_header("VERIFICANDO ENDPOINTS DE FORMULARIOS")
    
    results.append(("Faenas", test_faenas()))
    results.append(("Tipos de Equipo", test_tipos_equipo()))
    results.append(("Estados de Equipo", test_estados_equipo()))
    results.append(("Equipos", test_equipos()))
    results.append(("Tipos de Mantenimiento", test_tipos_mantenimiento()))
    results.append(("Usuarios", test_usuarios()))
    results.append(("Roles", test_roles()))
    
    print_header("RESUMEN")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}[OK]{Colors.END}" if result else f"{Colors.RED}[FAIL]{Colors.END}"
        print(f"  {name}: {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} pruebas pasaron{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[OK] Todos los endpoints funcionan correctamente!{Colors.END}")
        print(f"{Colors.CYAN}Los formularios del frontend pueden cargar datos del backend.{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}[FAIL] Algunos endpoints tienen problemas{Colors.END}")
        print(f"{Colors.YELLOW}Revisa los errores arriba y verifica el servidor.{Colors.END}\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[WARN] Prueba interrumpida{Colors.END}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}[ERROR] Error inesperado: {str(e)}{Colors.END}\n")
        sys.exit(1)

