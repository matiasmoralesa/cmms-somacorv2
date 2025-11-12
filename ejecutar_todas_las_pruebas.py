#!/usr/bin/env python3
"""
Ejecutar Todas las Pruebas
Script maestro que ejecuta todas las pruebas del sistema
"""
import subprocess
import sys
import time

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def run_test(script_name, description):
    print_header(f"🧪 {description}")
    print(f"Ejecutando: {script_name}")
    print("-" * 80)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        elapsed_time = time.time() - start_time
        
        # Mostrar output
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print("STDERR:", result.stderr)
        
        # Resultado
        if result.returncode == 0:
            print(f"\n✅ {description} - PASS ({elapsed_time:.2f}s)")
            return True, elapsed_time
        else:
            print(f"\n❌ {description} - FAIL ({elapsed_time:.2f}s)")
            return False, elapsed_time
    
    except subprocess.TimeoutExpired:
        print(f"\n⏱️  {description} - TIMEOUT (>60s)")
        return False, 60.0
    except Exception as e:
        print(f"\n❌ {description} - ERROR: {str(e)}")
        return False, 0.0

def main():
    print_header("🚀 SUITE COMPLETA DE PRUEBAS - CMMS SOMACOR V2")
    print("Ejecutando todas las pruebas del sistema...")
    print(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("verificar_configuracion_produccion.py", "Verificación de Configuración"),
        ("test_configuracion_seguridad.py", "Pruebas de Seguridad"),
        ("test_health_checks.py", "Pruebas de Health Checks"),
        ("test_integracion_completo.py", "Pruebas de Integración"),
    ]
    
    results = []
    total_time = 0
    
    for script, description in tests:
        success, elapsed = run_test(script, description)
        results.append((description, success, elapsed))
        total_time += elapsed
        time.sleep(1)  # Pequeña pausa entre pruebas
    
    # Resumen final
    print_header("📊 RESUMEN FINAL DE TODAS LAS PRUEBAS")
    
    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed
    
    print(f"\nTotal de suites de pruebas: {len(results)}")
    print(f"✅ Suites exitosas: {passed}")
    print(f"❌ Suites fallidas: {failed}")
    print(f"⏱️  Tiempo total: {total_time:.2f}s")
    print(f"📈 Porcentaje de éxito: {(passed/len(results))*100:.1f}%")
    
    print("\n" + "-" * 80)
    print("Detalle por suite:")
    print("-" * 80)
    
    for description, success, elapsed in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} | {elapsed:6.2f}s | {description}")
    
    print("-" * 80)
    
    if passed == len(results):
        print("\n🎉 ¡TODAS LAS SUITES DE PRUEBAS PASARON!")
        print("✅ El sistema está completamente verificado y listo para producción")
        print("\n📋 Próximos pasos:")
        print("   1. Configurar archivo .env con valores reales")
        print("   2. Generar SECRET_KEY única")
        print("   3. Configurar PostgreSQL")
        print("   4. Seguir GUIA_DESPLIEGUE_SEGURO.md")
        return 0
    else:
        print("\n⚠️  Algunas suites de pruebas fallaron")
        print("❌ Revisa los errores antes de continuar")
        print("\n📋 Acciones recomendadas:")
        print("   1. Revisar los logs de las pruebas fallidas")
        print("   2. Verificar la configuración del sistema")
        print("   3. Consultar ANALISIS_PRODUCCION_COMPLETO.md")
        return 1

if __name__ == '__main__':
    sys.exit(main())
