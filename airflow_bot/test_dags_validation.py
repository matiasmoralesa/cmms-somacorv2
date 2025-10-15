"""
Script de validación de DAGs de Airflow
Verifica que los DAGs se puedan importar y no tengan errores de sintaxis
"""

import sys
from pathlib import Path
import importlib.util
from datetime import datetime

print("=" * 80)
print("VALIDACIÓN DE DAGs DE AIRFLOW")
print("=" * 80)
print()

dags_dir = Path(__file__).parent / 'dags'
dag_files = list(dags_dir.glob('dag_*.py'))

print(f"DAGs a validar: {len(dag_files)}")
print()

resultados = []

for dag_file in dag_files:
    print(f"Validando: {dag_file.name}")
    print("-" * 80)
    
    try:
        # Cargar el módulo
        spec = importlib.util.spec_from_file_location(dag_file.stem, dag_file)
        module = importlib.util.module_from_spec(spec)
        
        # Ejecutar el módulo
        spec.loader.exec_module(module)
        
        # Verificar que tenga la variable dag_instance
        if hasattr(module, 'dag_instance'):
            dag_instance = module.dag_instance
            print(f"✅ DAG cargado correctamente")
            print(f"   DAG ID: {dag_instance.dag_id}")
            print(f"   Schedule: {dag_instance.schedule_interval}")
            print(f"   Tags: {dag_instance.tags}")
            
            # Contar tareas
            num_tasks = len(dag_instance.tasks)
            print(f"   Tareas: {num_tasks}")
            
            resultados.append({
                'archivo': dag_file.name,
                'dag_id': dag_instance.dag_id,
                'tareas': num_tasks,
                'status': 'PASS'
            })
        else:
            print(f"⚠️  DAG cargado pero no se encontró 'dag_instance'")
            resultados.append({
                'archivo': dag_file.name,
                'dag_id': 'N/A',
                'tareas': 0,
                'status': 'WARNING'
            })
        
    except Exception as e:
        print(f"❌ Error al cargar DAG: {str(e)}")
        resultados.append({
            'archivo': dag_file.name,
            'dag_id': 'N/A',
            'tareas': 0,
            'status': 'FAIL',
            'error': str(e)
        })
    
    print()

# Resumen
print("=" * 80)
print("RESUMEN DE VALIDACIÓN")
print("=" * 80)
print()

passed = sum(1 for r in resultados if r['status'] == 'PASS')
warnings = sum(1 for r in resultados if r['status'] == 'WARNING')
failed = sum(1 for r in resultados if r['status'] == 'FAIL')

print(f"Total DAGs: {len(resultados)}")
print(f"  ✅ PASS: {passed}")
print(f"  ⚠️  WARNING: {warnings}")
print(f"  ❌ FAIL: {failed}")
print()

if failed == 0:
    print("✅ Todos los DAGs son válidos y están listos para ejecutarse en Airflow")
else:
    print("❌ Algunos DAGs tienen errores que deben corregirse")
    print()
    print("DAGs con errores:")
    for r in resultados:
        if r['status'] == 'FAIL':
            print(f"  - {r['archivo']}: {r.get('error', 'Error desconocido')}")

print()

