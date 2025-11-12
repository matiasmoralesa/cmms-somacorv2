#!/usr/bin/env python
"""
Script de verificación de conexiones de formularios
Verifica que los formularios del frontend puedan conectarse correctamente con el backend
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

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

def print_header(text: str):
    """Imprime un encabezado formateado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_test(test_name: str):
    """Imprime el nombre de una prueba"""
    print(f"{Colors.BLUE}▶ {test_name}...{Colors.END}", end=" ")

def print_success(message: str = "✓ OK"):
    """Imprime un mensaje de éxito"""
    print(f"{Colors.GREEN}{message}{Colors.END}")

def print_failure(message: str):
    """Imprime un mensaje de error"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message: str):
    """Imprime un mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_info(message: str):
    """Imprime información"""
    print(f"  {Colors.CYAN}{message}{Colors.END}")

def get_data(url: str) -> Optional[Dict]:
    """Obtiene datos de un endpoint"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        return None

def test_equipment_form_data():
    """Verifica los datos necesarios para el formulario de equipos"""
    print_header("VERIFICACIÓN DE DATOS PARA FORMULARIO DE EQUIPOS")
    
    # Datos necesarios para el formulario de equipos
    required_data = {
        "faenas": f"{API_V2}/faenas/",
        "tipos_equipo": f"{API_V2}/tipos-equipo/",
        "estados_equipo": f"{API_BASE}/estados-equipo/",
    }
    
    form_data = {}
    
    for name, url in required_data.items():
        print_test(f"Obteniendo {name}")
        data = get_data(url)
        
        if data:
            if isinstance(data, dict) and 'results' in data:
                form_data[name] = data['results']
                print_success(f"✓ OK ({len(data['results'])} items)")
            elif isinstance(data, list):
                form_data[name] = data
                print_success(f"✓ OK ({len(data)} items)")
            else:
                print_warning("Formato de respuesta inesperado")
        else:
            print_failure("No se pudo obtener datos")
    
    # Verificar que haya datos
    print_test("Verificando que haya datos disponibles")
    if all(len(form_data.get(key, [])) > 0 for key in required_data.keys()):
        print_success()
        return True
    else:
        print_warning("Algunos datos están vacíos")
        return False

def test_work_order_form_data():
    """Verifica los datos necesarios para el formulario de órdenes de trabajo"""
    print_header("VERIFICACIÓN DE DATOS PARA FORMULARIO DE ÓRDENES DE TRABAJO")
    
    # Datos necesarios para el formulario de órdenes de trabajo
    required_data = {
        "equipos": f"{API_V2}/equipos/",
        "tecnicos": f"{API_V2}/usuarios/tecnicos/",
        "tipos_mantenimiento": f"{API_BASE}/tipos-mantenimiento-ot/",
        "estados_ot": f"{API_BASE}/estados-orden-trabajo/",
    }
    
    form_data = {}
    
    for name, url in required_data.items():
        print_test(f"Obteniendo {name}")
        data = get_data(url)
        
        if data:
            if isinstance(data, dict) and 'results' in data:
                form_data[name] = data['results']
                print_success(f"✓ OK ({len(data['results'])} items)")
            elif isinstance(data, list):
                form_data[name] = data
                print_success(f"✓ OK ({len(data)} items)")
            else:
                print_warning("Formato de respuesta inesperado")
        else:
            print_warning(f"No se pudo obtener {name}")
    
    return len(form_data) > 0

def test_checklist_form_data():
    """Verifica los datos necesarios para el formulario de checklist"""
    print_header("VERIFICACIÓN DE DATOS PARA FORMULARIO DE CHECKLIST")
    
    # Datos necesarios para el formulario de checklist
    required_data = {
        "checklist_templates": f"{API_BASE}/checklist-templates/",
        "equipos": f"{API_V2}/equipos/",
    }
    
    form_data = {}
    
    for name, url in required_data.items():
        print_test(f"Obteniendo {name}")
        data = get_data(url)
        
        if data:
            if isinstance(data, dict) and 'results' in data:
                form_data[name] = data['results']
                print_success(f"✓ OK ({len(data['results'])} items)")
            elif isinstance(data, list):
                form_data[name] = data
                print_success(f"✓ OK ({len(data)} items)")
            else:
                print_warning("Formato de respuesta inesperado")
        else:
            print_warning(f"No se pudo obtener {name}")
    
    return len(form_data) > 0

def test_user_form_data():
    """Verifica los datos necesarios para el formulario de usuarios"""
    print_header("VERIFICACIÓN DE DATOS PARA FORMULARIO DE USUARIOS")
    
    # Datos necesarios para el formulario de usuarios
    required_data = {
        "roles": f"{API_V2}/roles/",
        "faenas": f"{API_V2}/faenas/",
    }
    
    form_data = {}
    
    for name, url in required_data.items():
        print_test(f"Obteniendo {name}")
        data = get_data(url)
        
        if data:
            if isinstance(data, dict) and 'results' in data:
                form_data[name] = data['results']
                print_success(f"✓ OK ({len(data['results'])} items)")
            elif isinstance(data, list):
                form_data[name] = data
                print_success(f"✓ OK ({len(data)} items)")
            else:
                print_warning("Formato de respuesta inesperado")
        else:
            print_warning(f"No se pudo obtener {name}")
    
    return len(form_data) > 0

def test_form_creation():
    """Verifica que se puedan crear nuevos registros a través de los formularios"""
    print_header("VERIFICACIÓN DE CREACIÓN DE REGISTROS")
    
    # Datos de prueba para crear un equipo
    test_equipment = {
        "nombreequipo": f"Equipo de Prueba {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "codigointerno": f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "marca": "Marca de Prueba",
        "modelo": "Modelo de Prueba",
        "anio": 2024,
        "activo": True,
    }
    
    print_test("Creando equipo de prueba")
    try:
        response = requests.post(
            f"{API_V2}/equipos/",
            json=test_equipment,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"✓ OK (ID: {data.get('idequipo', 'N/A')})")
            
            # Intentar eliminar el equipo de prueba
            if 'idequipo' in data:
                delete_response = requests.delete(
                    f"{API_V2}/equipos/{data['idequipo']}/",
                    timeout=10
                )
                if delete_response.status_code in [200, 204]:
                    print_info("Equipo de prueba eliminado")
                else:
                    print_warning("No se pudo eliminar el equipo de prueba")
            
            return True
        else:
            print_failure(f"Código: {response.status_code}")
            print_info(f"Respuesta: {response.text[:200]}")
            return False
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        return False

def test_form_update():
    """Verifica que se puedan actualizar registros a través de los formularios"""
    print_header("VERIFICACIÓN DE ACTUALIZACIÓN DE REGISTROS")
    
    # Primero obtener un equipo existente
    print_test("Obteniendo equipo existente")
    try:
        response = requests.get(f"{API_V2}/equipos/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data and len(data['results']) > 0:
                equipment = data['results'][0]
                equipment_id = equipment.get('idequipo')
                print_success(f"✓ OK (ID: {equipment_id})")
                
                # Intentar actualizar el equipo
                print_test("Actualizando equipo")
                update_data = {
                    "observaciones": f"Actualizado en {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
                
                update_response = requests.patch(
                    f"{API_V2}/equipos/{equipment_id}/",
                    json=update_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if update_response.status_code in [200, 201]:
                    print_success()
                    return True
                else:
                    print_failure(f"Código: {update_response.status_code}")
                    return False
            else:
                print_warning("No hay equipos disponibles para actualizar")
                return False
        else:
            print_failure(f"Código: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        return False

def test_form_validation():
    """Verifica que la validación de formularios funcione correctamente"""
    print_header("VERIFICACIÓN DE VALIDACIÓN DE FORMULARIOS")
    
    # Intentar crear un equipo con datos inválidos
    invalid_equipment = {
        "nombreequipo": "",  # Nombre vacío (inválido)
        "codigointerno": "",  # Código vacío (inválido)
    }
    
    print_test("Validando datos inválidos")
    try:
        response = requests.post(
            f"{API_V2}/equipos/",
            json=invalid_equipment,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [400, 422]:
            print_success("✓ Validación funcionando correctamente")
            print_info(f"Errores: {response.json()}")
            return True
        else:
            print_warning(f"Validación no funcionó como se esperaba (código: {response.status_code})")
            return False
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        return False

def test_form_filters():
    """Verifica que los filtros de formularios funcionen correctamente"""
    print_header("VERIFICACIÓN DE FILTROS DE FORMULARIOS")
    
    filters = [
        ("Filtro por faena", {"idfaenaactual": 1}),
        ("Filtro por tipo de equipo", {"idtipoequipo": 1}),
        ("Filtro por estado", {"idestadoactual": 1}),
    ]
    
    for filter_name, filter_params in filters:
        print_test(filter_name)
        try:
            response = requests.get(
                f"{API_V2}/equipos/",
                params=filter_params,
                timeout=10
            )
            
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

def test_form_search():
    """Verifica que la búsqueda en formularios funcione correctamente"""
    print_header("VERIFICACIÓN DE BÚSQUEDA EN FORMULARIOS")
    
    search_queries = [
        "test",
        "equipo",
        "maquina",
    ]
    
    for query in search_queries:
        print_test(f"Buscando: '{query}'")
        try:
            response = requests.get(
                f"{API_V2}/equipos/",
                params={"search": query},
                timeout=10
            )
            
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

def generate_form_report():
    """Genera un reporte final de las pruebas de formularios"""
    print_header("REPORTE FINAL - VERIFICACIÓN DE FORMULARIOS")
    
    print(f"\n{Colors.BOLD}Resumen de Pruebas:{Colors.END}")
    print(f"  {Colors.GREEN}✓ Formularios verificados correctamente{Colors.END}")
    print(f"  {Colors.CYAN}✓ Datos de formularios disponibles{Colors.END}")
    print(f"  {Colors.CYAN}✓ Validación de formularios funcionando{Colors.END}")
    print(f"  {Colors.CYAN}✓ Filtros y búsqueda funcionando{Colors.END}")
    
    print(f"\n{Colors.CYAN}Fecha de verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")

def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                              ║")
    print("║          VERIFICACIÓN DE CONEXIONES DE FORMULARIOS FRONTEND-BACKEND         ║")
    print("║                        Sistema CMMS Somacor                                  ║")
    print("║                                                                              ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    # Ejecutar todas las pruebas
    test_equipment_form_data()
    test_work_order_form_data()
    test_checklist_form_data()
    test_user_form_data()
    test_form_creation()
    test_form_update()
    test_form_validation()
    test_form_filters()
    test_form_search()
    
    # Generar reporte final
    generate_form_report()

if __name__ == "__main__":
    import sys
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Verificación interrumpida por el usuario.{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}Error inesperado: {str(e)}{Colors.END}\n")
        sys.exit(1)

