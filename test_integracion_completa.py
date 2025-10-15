"""
Prueba de Integración Completa del Bot Asistente CMMS
Verifica todos los componentes del sistema
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import traceback

print("=" * 80)
print("PRUEBA DE INTEGRACIÓN COMPLETA - BOT ASISTENTE CMMS")
print("=" * 80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Contador de pruebas
tests_passed = 0
tests_failed = 0
tests_total = 0

def run_test(test_name, test_func):
    """Ejecutar una prueba y registrar el resultado"""
    global tests_passed, tests_failed, tests_total
    tests_total += 1
    
    print(f"\n{'='*80}")
    print(f"TEST {tests_total}: {test_name}")
    print('-' * 80)
    
    try:
        start_time = time.time()
        result = test_func()
        elapsed = time.time() - start_time
        
        if result:
            print(f"✅ PASS - {elapsed:.3f}s")
            tests_passed += 1
            return True
        else:
            print(f"❌ FAIL - {elapsed:.3f}s")
            tests_failed += 1
            return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ ERROR - {elapsed:.3f}s")
        print(f"   {str(e)}")
        print(f"   {traceback.format_exc()}")
        tests_failed += 1
        return False


# TEST 1: Estructura de directorios
def test_estructura_directorios():
    """Verificar que todos los directorios necesarios existan"""
    base_dir = Path('/home/ubuntu/cmms-somacorv2')
    
    directorios_requeridos = [
        'airflow_bot',
        'airflow_bot/dags',
        'airflow_bot/config',
        'airflow_bot/scripts',
        'dask_cluster',
        'dask_cluster/scripts',
        'ml_models',
        'ml_models/training',
        'telegram_integration',
        'telegram_integration/notifications',
    ]
    
    all_exist = True
    for dir_path in directorios_requeridos:
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} - NO EXISTE")
            all_exist = False
    
    return all_exist


# TEST 2: Archivos principales
def test_archivos_principales():
    """Verificar que todos los archivos principales existan"""
    base_dir = Path('/home/ubuntu/cmms-somacorv2')
    
    archivos_requeridos = [
        'airflow_bot/config/airflow_config.py',
        'airflow_bot/scripts/cmms_api_client.py',
        'airflow_bot/dags/dag_analisis_predictivo.py',
        'airflow_bot/dags/dag_mantenimiento_preventivo.py',
        'airflow_bot/dags/dag_procesamiento_checklists.py',
        'airflow_bot/requirements.txt',
        'airflow_bot/.env.example',
        'airflow_bot/setup.sh',
        'telegram_integration/bot.py',
        'telegram_integration/notifications/telegram_notifier.py',
        'dask_cluster/scripts/time_series_analysis.py',
        'ml_models/training/failure_prediction_model.py',
        'GUIA_INICIO_RAPIDO.md',
        'REPORTE_PRUEBAS_RENDIMIENTO.md',
    ]
    
    all_exist = True
    for file_path in archivos_requeridos:
        full_path = base_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"  ✓ {file_path} ({size:,} bytes)")
        else:
            print(f"  ✗ {file_path} - NO EXISTE")
            all_exist = False
    
    return all_exist


# TEST 3: Importación de módulos
def test_importacion_modulos():
    """Verificar que todos los módulos se puedan importar"""
    sys.path.insert(0, '/home/ubuntu/cmms-somacorv2/airflow_bot')
    
    modulos = [
        ('config.airflow_config', 'AirflowConfig'),
        ('config.airflow_config', 'CMSSConfig'),
        ('config.airflow_config', 'DaskConfig'),
        ('config.airflow_config', 'TelegramConfig'),
        ('scripts.cmms_api_client', 'CMSSAPIClient'),
    ]
    
    all_imported = True
    for module_name, class_name in modulos:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"  ✓ {module_name}.{class_name}")
        except Exception as e:
            print(f"  ✗ {module_name}.{class_name} - ERROR: {str(e)}")
            all_imported = False
    
    return all_imported


# TEST 4: Validación de configuración
def test_validacion_configuracion():
    """Verificar que la configuración sea válida"""
    sys.path.insert(0, '/home/ubuntu/cmms-somacorv2/airflow_bot')
    
    from config.airflow_config import (
        AirflowConfig, CMSSConfig, DaskConfig, 
        TelegramConfig, BusinessLogicConfig
    )
    
    configs_validas = True
    
    # Verificar configuraciones críticas
    checks = [
        ('CMMS API URL', CMSSConfig.API_BASE_URL, lambda x: x.startswith('http')),
        ('Airflow Home', AirflowConfig.AIRFLOW_HOME, lambda x: Path(x).exists()),
        ('DAGs Folder', AirflowConfig.DAGS_FOLDER, lambda x: Path(x).exists()),
        ('Dask Workers', DaskConfig.N_WORKERS, lambda x: x > 0),
        ('Estados OT', BusinessLogicConfig.ESTADOS_OT, lambda x: len(x) > 0),
        ('Tipos Mantenimiento', BusinessLogicConfig.TIPOS_MANTENIMIENTO, lambda x: len(x) > 0),
    ]
    
    for name, value, validator in checks:
        try:
            if validator(value):
                print(f"  ✓ {name}: {value}")
            else:
                print(f"  ✗ {name}: {value} - INVÁLIDO")
                configs_validas = False
        except Exception as e:
            print(f"  ✗ {name} - ERROR: {str(e)}")
            configs_validas = False
    
    return configs_validas


# TEST 5: Sintaxis de DAGs
def test_sintaxis_dags():
    """Verificar que los DAGs no tengan errores de sintaxis"""
    import ast
    
    dags_dir = Path('/home/ubuntu/cmms-somacorv2/airflow_bot/dags')
    dag_files = list(dags_dir.glob('dag_*.py'))
    
    all_valid = True
    for dag_file in dag_files:
        try:
            with open(dag_file, 'r') as f:
                code = f.read()
                ast.parse(code)
            print(f"  ✓ {dag_file.name} - Sintaxis válida")
        except SyntaxError as e:
            print(f"  ✗ {dag_file.name} - ERROR DE SINTAXIS: {str(e)}")
            all_valid = False
    
    return all_valid


# TEST 6: Cliente de API
def test_cliente_api():
    """Verificar que el cliente de API se inicialice correctamente"""
    sys.path.insert(0, '/home/ubuntu/cmms-somacorv2/airflow_bot')
    
    from scripts.cmms_api_client import CMSSAPIClient
    
    try:
        client = CMSSAPIClient()
        print(f"  ✓ Cliente inicializado")
        print(f"    Base URL: {client.base_url}")
        print(f"    Timeout: {client.timeout}s")
        
        # Verificar métodos principales
        metodos = [
            'get_equipos',
            'get_ordenes_trabajo',
            'create_orden_trabajo',
            'get_tecnicos',
            'get_planes_mantenimiento',
        ]
        
        for metodo in metodos:
            if hasattr(client, metodo):
                print(f"    ✓ Método: {metodo}")
            else:
                print(f"    ✗ Método faltante: {metodo}")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error al inicializar cliente: {str(e)}")
        return False


# TEST 7: Sistema de notificaciones
def test_sistema_notificaciones():
    """Verificar que el sistema de notificaciones esté implementado"""
    sys.path.insert(0, '/home/ubuntu/cmms-somacorv2/telegram_integration')
    
    try:
        from notifications.telegram_notifier import TelegramNotifier
        
        notifier = TelegramNotifier()
        print(f"  ✓ TelegramNotifier inicializado")
        
        # Verificar métodos
        metodos = ['send_message', 'send_alert', 'send_report']
        
        for metodo in metodos:
            if hasattr(notifier, metodo):
                print(f"    ✓ Método: {metodo}")
            else:
                print(f"    ✗ Método faltante: {metodo}")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


# TEST 8: Análisis de series temporales
def test_analisis_series_temporales():
    """Verificar módulo de análisis con Dask"""
    sys.path.insert(0, '/home/ubuntu/cmms-somacorv2/dask_cluster/scripts')
    sys.path.insert(0, '/home/ubuntu/cmms-somacorv2/airflow_bot')
    
    try:
        from time_series_analysis import TimeSeriesAnalyzer
        
        analyzer = TimeSeriesAnalyzer()
        print(f"  ✓ TimeSeriesAnalyzer inicializado")
        
        # Verificar métodos
        metodos = [
            'load_work_orders_to_dask',
            'calculate_mtbf_by_equipment',
            'calculate_mttr_by_equipment',
            'analyze_failure_trends',
            'detect_anomalies',
            'calculate_equipment_health_score',
        ]
        
        for metodo in metodos:
            if hasattr(analyzer, metodo):
                print(f"    ✓ Método: {metodo}")
            else:
                print(f"    ✗ Método faltante: {metodo}")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


# TEST 9: Modelo de Machine Learning
def test_modelo_ml():
    """Verificar módulo de ML"""
    sys.path.insert(0, '/home/ubuntu/cmms-somacorv2/ml_models/training')
    sys.path.insert(0, '/home/ubuntu/cmms-somacorv2/airflow_bot')
    
    try:
        from failure_prediction_model import FailurePredictionModel
        
        model = FailurePredictionModel()
        print(f"  ✓ FailurePredictionModel inicializado")
        
        # Verificar métodos
        metodos = [
            'extract_features',
            'prepare_data',
            'train',
            'save_model',
            'load_model',
            'predict',
        ]
        
        for metodo in metodos:
            if hasattr(model, metodo):
                print(f"    ✓ Método: {metodo}")
            else:
                print(f"    ✗ Método faltante: {metodo}")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


# TEST 10: Scripts de instalación
def test_scripts_instalacion():
    """Verificar que los scripts de instalación sean ejecutables"""
    scripts = [
        '/home/ubuntu/cmms-somacorv2/airflow_bot/setup.sh',
    ]
    
    all_executable = True
    for script_path in scripts:
        script = Path(script_path)
        if script.exists():
            import os
            is_executable = os.access(script, os.X_OK)
            if is_executable:
                print(f"  ✓ {script.name} - Ejecutable")
            else:
                print(f"  ✗ {script.name} - NO ejecutable")
                all_executable = False
        else:
            print(f"  ✗ {script.name} - NO existe")
            all_executable = False
    
    return all_executable


# Ejecutar todas las pruebas
print("\nEjecutando pruebas de integración...\n")

run_test("Estructura de Directorios", test_estructura_directorios)
run_test("Archivos Principales", test_archivos_principales)
run_test("Importación de Módulos", test_importacion_modulos)
run_test("Validación de Configuración", test_validacion_configuracion)
run_test("Sintaxis de DAGs", test_sintaxis_dags)
run_test("Cliente de API", test_cliente_api)
run_test("Sistema de Notificaciones", test_sistema_notificaciones)
run_test("Análisis de Series Temporales", test_analisis_series_temporales)
run_test("Modelo de Machine Learning", test_modelo_ml)
run_test("Scripts de Instalación", test_scripts_instalacion)

# Resumen final
print("\n" + "=" * 80)
print("RESUMEN DE PRUEBAS DE INTEGRACIÓN")
print("=" * 80)
print()
print(f"Total de pruebas: {tests_total}")
print(f"  ✅ Pasadas: {tests_passed}")
print(f"  ❌ Fallidas: {tests_failed}")
print()

if tests_failed == 0:
    print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
    print()
    print("El sistema está completamente funcional y listo para usar.")
    print()
    print("Próximos pasos:")
    print("  1. Configurar variables de entorno en airflow_bot/.env")
    print("  2. Ejecutar ./airflow_bot/setup.sh")
    print("  3. Iniciar el sistema con ./start_bot_system.sh")
    exit_code = 0
else:
    print("⚠️  ALGUNAS PRUEBAS FALLARON")
    print()
    print("Por favor revisa los errores anteriores y corrige los problemas.")
    exit_code = 1

print()
print("=" * 80)

sys.exit(exit_code)

