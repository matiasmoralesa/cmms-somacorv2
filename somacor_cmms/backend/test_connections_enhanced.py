#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de verificación completa de conexiones Frontend-Backend (Versión Mejorada)
Verifica que todos los endpoints estén funcionando correctamente
Incluye: Logging detallado, exportación de resultados, dashboard HTML
"""

import requests
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

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

# Estructura de resultados
results = {
    'timestamp': datetime.now().isoformat(),
    'passed': 0,
    'failed': 0,
    'warnings': 0,
    'total': 0,
    'tests': [],
    'summary': {}
}

# Configuración de logging
LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f'connection_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

def log(message: str, level: str = 'INFO'):
    """Registra mensajes en el log"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] [{level}] {message}\n"
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_message)
    except Exception as e:
        print(f"Error escribiendo log: {e}")

def print_header(text: str):
    """Imprime un encabezado formateado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")
    log(text, 'HEADER')

def print_test(test_name: str):
    """Imprime el nombre de una prueba"""
    print(f"{Colors.BLUE}[*] {test_name}...{Colors.END}", end=" ")
    log(f"Ejecutando: {test_name}", 'TEST')

def print_success(message: str = "[OK]"):
    """Imprime un mensaje de éxito"""
    print(f"{Colors.GREEN}{message}{Colors.END}")
    results['passed'] += 1
    results['total'] += 1
    log(f"Exitoso: {message}", 'SUCCESS')

def print_failure(message: str):
    """Imprime un mensaje de error"""
    print(f"{Colors.RED}[FAIL] {message}{Colors.END}")
    results['failed'] += 1
    results['total'] += 1
    log(f"Fallido: {message}", 'ERROR')

def print_warning(message: str):
    """Imprime un mensaje de advertencia"""
    print(f"{Colors.YELLOW}[WARN] {message}{Colors.END}")
    results['warnings'] += 1
    log(f"Advertencia: {message}", 'WARNING')

def print_info(message: str):
    """Imprime información"""
    print(f"  {Colors.CYAN}{message}{Colors.END}")
    log(f"Info: {message}", 'INFO')

def record_test(name: str, status: str, details: Dict):
    """Registra el resultado de una prueba"""
    test_result = {
        'name': name,
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'details': details
    }
    results['tests'].append(test_result)

def test_connection():
    """Prueba la conexión básica al servidor"""
    print_header("VERIFICACION DE CONEXION BASICA")
    
    print_test("Conexion al servidor Django")
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print_success()
            record_test("Conexion al servidor", "PASSED", {"status_code": response.status_code})
            return True
        else:
            print_failure(f"Codigo de estado: {response.status_code}")
            record_test("Conexion al servidor", "FAILED", {"status_code": response.status_code})
            return False
    except requests.exceptions.ConnectionError:
        print_failure("No se puede conectar al servidor. ¿Esta corriendo en http://localhost:8000?")
        record_test("Conexion al servidor", "FAILED", {"error": "ConnectionError"})
        return False
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        record_test("Conexion al servidor", "FAILED", {"error": str(e)})
        return False

def test_api_endpoints():
    """Prueba los endpoints de la API"""
    print_header("VERIFICACION DE ENDPOINTS DE LA API")
    
    endpoints = [
        ("API Root", f"{API_BASE}/"),
        ("Faenas", f"{API_BASE}/faenas/"),
        ("Tipos de Equipo", f"{API_BASE}/tipos-equipo/"),
        ("Estados de Equipo", f"{API_BASE}/estados-equipo/"),
        ("Roles", f"{API_BASE}/roles/"),
        ("Equipos V2", f"{API_V2}/equipos/"),
        ("Ordenes de Trabajo V2", f"{API_V2}/ordenes-trabajo/"),
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
                    print_success(f"[OK] ({count} items)")
                    record_test(name, "PASSED", {"status_code": 200, "count": count})
                elif isinstance(data, list):
                    print_success(f"[OK] ({len(data)} items)")
                    record_test(name, "PASSED", {"status_code": 200, "count": len(data)})
                else:
                    print_success()
                    record_test(name, "PASSED", {"status_code": 200})
            elif response.status_code == 401:
                print_warning("Requiere autenticacion (esperado)")
                record_test(name, "WARNING", {"status_code": 401, "message": "Requiere autenticacion"})
            elif response.status_code == 404:
                print_failure("Endpoint no encontrado")
                record_test(name, "FAILED", {"status_code": 404})
            else:
                print_failure(f"Codigo: {response.status_code}")
                record_test(name, "FAILED", {"status_code": response.status_code})
        except requests.exceptions.Timeout:
            print_failure("Timeout")
            record_test(name, "FAILED", {"error": "Timeout"})
        except Exception as e:
            print_failure(f"Error: {str(e)}")
            record_test(name, "FAILED", {"error": str(e)})

def test_cors_configuration():
    """Verifica la configuración de CORS"""
    print_header("VERIFICACION DE CONFIGURACION CORS")
    
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
            print_info(f"Metodos permitidos: {cors_headers['Access-Control-Allow-Methods']}")
            record_test("CORS Configuration", "PASSED", cors_headers)
        else:
            print_warning("CORS no configurado correctamente")
            record_test("CORS Configuration", "WARNING", {"message": "CORS no configurado"})
    except Exception as e:
        print_failure(f"Error: {str(e)}")
        record_test("CORS Configuration", "FAILED", {"error": str(e)})

def test_data_consistency():
    """Verifica la consistencia de los datos"""
    print_header("VERIFICACION DE CONSISTENCIA DE DATOS")
    
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
                        print_success(f"[OK] ({len(data['results'])} registros)")
                        record_test(f"Datos de {name}", "PASSED", {"count": len(data['results'])})
                    else:
                        print_warning(f"No hay datos de {name}")
                        record_test(f"Datos de {name}", "WARNING", {"message": "No hay datos"})
                else:
                    print_warning(f"Formato de respuesta inesperado")
                    record_test(f"Datos de {name}", "WARNING", {"message": "Formato inesperado"})
            else:
                print_failure(f"Codigo: {response.status_code}")
                record_test(f"Datos de {name}", "FAILED", {"status_code": response.status_code})
        except Exception as e:
            print_failure(f"Error: {str(e)}")
            record_test(f"Datos de {name}", "FAILED", {"error": str(e)})

def export_results():
    """Exporta los resultados a JSON y genera dashboard HTML"""
    print_header("EXPORTANDO RESULTADOS")
    
    # Exportar a JSON
    json_file = LOG_DIR / f'results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print_info(f"Resultados exportados a: {json_file}")
        log(f"Resultados exportados a: {json_file}", 'INFO')
    except Exception as e:
        print_warning(f"Error exportando a JSON: {e}")
    
    # Generar dashboard HTML
    html_file = LOG_DIR / f'dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    try:
        generate_html_dashboard(html_file)
        print_info(f"Dashboard generado en: {html_file}")
        log(f"Dashboard generado en: {html_file}", 'INFO')
    except Exception as e:
        print_warning(f"Error generando dashboard: {e}")

def generate_html_dashboard(html_file: Path):
    """Genera un dashboard HTML con los resultados"""
    total_tests = results['passed'] + results['failed']
    success_rate = (results['passed'] / total_tests * 100) if total_tests > 0 else 0
    
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Verificación de Conexiones CMMS</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 30px; }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        .subtitle {{ color: #666; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .stat-card.success {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .stat-card.error {{ background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%); }}
        .stat-card.warning {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .stat-card.info {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .stat-value {{ font-size: 48px; font-weight: bold; margin-bottom: 10px; }}
        .stat-label {{ font-size: 14px; opacity: 0.9; }}
        .progress-bar {{ background: #e0e0e0; border-radius: 10px; height: 30px; margin: 20px 0; overflow: hidden; }}
        .progress-fill {{ background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%); height: 100%; transition: width 0.3s ease; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }}
        .tests {{ margin-top: 30px; }}
        .test-item {{ background: #f9f9f9; padding: 15px; margin-bottom: 10px; border-radius: 5px; border-left: 4px solid #ddd; }}
        .test-item.passed {{ border-left-color: #38ef7d; }}
        .test-item.failed {{ border-left-color: #ee0979; }}
        .test-item.warning {{ border-left-color: #f5576c; }}
        .test-name {{ font-weight: bold; color: #333; }}
        .test-status {{ display: inline-block; padding: 3px 10px; border-radius: 3px; font-size: 12px; margin-left: 10px; }}
        .test-status.passed {{ background: #38ef7d; color: white; }}
        .test-status.failed {{ background: #ee0979; color: white; }}
        .test-status.warning {{ background: #f5576c; color: white; }}
        .test-details {{ margin-top: 5px; font-size: 12px; color: #666; }}
        .timestamp {{ text-align: center; color: #999; margin-top: 30px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Dashboard - Verificación de Conexiones CMMS</h1>
        <p class="subtitle">Sistema CMMS Somacor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="stats">
            <div class="stat-card info">
                <div class="stat-value">{results['total']}</div>
                <div class="stat-label">Total de Pruebas</div>
            </div>
            <div class="stat-card success">
                <div class="stat-value">{results['passed']}</div>
                <div class="stat-label">Exitosas</div>
            </div>
            <div class="stat-card error">
                <div class="stat-value">{results['failed']}</div>
                <div class="stat-label">Fallidas</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-value">{results['warnings']}</div>
                <div class="stat-label">Advertencias</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {success_rate}%">{success_rate:.1f}%</div>
        </div>
        
        <div class="tests">
            <h2>Detalles de las Pruebas</h2>
"""
    
    for test in results['tests']:
        status_class = test['status'].lower()
        html_content += f"""
            <div class="test-item {status_class}">
                <div class="test-name">{test['name']}
                    <span class="test-status {status_class}">{test['status']}</span>
                </div>
                <div class="test-details">
                    <strong>Timestamp:</strong> {test['timestamp']}<br>
                    <strong>Detalles:</strong> {json.dumps(test['details'], ensure_ascii=False)}
                </div>
            </div>
"""
    
    html_content += f"""
        </div>
        
        <div class="timestamp">
            Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_report():
    """Genera un reporte final"""
    print_header("REPORTE FINAL")
    
    total_tests = results['passed'] + results['failed']
    success_rate = (results['passed'] / total_tests * 100) if total_tests > 0 else 0
    
    results['summary'] = {
        'total_tests': total_tests,
        'passed': results['passed'],
        'failed': results['failed'],
        'warnings': results['warnings'],
        'success_rate': success_rate
    }
    
    print(f"\n{Colors.BOLD}Resumen de Pruebas:{Colors.END}")
    print(f"  {Colors.GREEN}[OK] Exitosas: {results['passed']}{Colors.END}")
    print(f"  {Colors.RED}[FAIL] Fallidas: {results['failed']}{Colors.END}")
    print(f"  {Colors.YELLOW}[WARN] Advertencias: {results['warnings']}{Colors.END}")
    print(f"  Total: {total_tests}")
    print(f"\n{Colors.BOLD}Tasa de exito: {success_rate:.1f}%{Colors.END}")
    
    if results['failed'] == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[OK] Todas las pruebas pasaron exitosamente!{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}[FAIL] Algunas pruebas fallaron. Revisa los errores arriba.{Colors.END}")
    
    print(f"\n{Colors.CYAN}Fecha de verificacion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")
    
    log(f"Reporte final: {results['passed']} exitosas, {results['failed']} fallidas, {results['warnings']} advertencias", 'INFO')

def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("="*80)
    print("          VERIFICACION COMPLETA DE CONEXIONES FRONTEND-BACKEND".center(80))
    print("                        Sistema CMMS Somacor (Version Mejorada)".center(80))
    print("="*80)
    print(f"{Colors.END}\n")
    
    log("Iniciando verificacion completa de conexiones", 'INFO')
    
    # Ejecutar todas las pruebas
    if not test_connection():
        print(f"\n{Colors.RED}{Colors.BOLD}[FAIL] No se pudo conectar al servidor. Por favor, inicia el servidor primero.{Colors.END}")
        print(f"{Colors.YELLOW}Ejecuta: python manage.py runserver{Colors.END}\n")
        log("Fallo en conexion inicial al servidor", 'ERROR')
        sys.exit(1)
    
    test_api_endpoints()
    test_cors_configuration()
    test_data_consistency()
    
    # Exportar resultados
    export_results()
    
    # Generar reporte final
    generate_report()
    
    log("Verificacion completada", 'INFO')
    
    return 0 if results['failed'] == 0 else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[WARN] Verificacion interrumpida{Colors.END}\n")
        log("Verificacion interrumpida por el usuario", 'WARNING')
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}[ERROR] Error inesperado: {str(e)}{Colors.END}\n")
        log(f"Error inesperado: {str(e)}", 'ERROR')
        sys.exit(1)

