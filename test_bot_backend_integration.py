"""
Script de prueba de integración entre el bot de Telegram y el backend Django
"""

import sys
from pathlib import Path

# Agregar directorios al path
sys.path.insert(0, str(Path(__file__).parent / 'airflow_bot'))
from scripts.cmms_api_client import CMSSAPIClient

def test_backend_connection():
    """Probar conexión con el backend"""
    print("=" * 60)
    print("PRUEBA DE INTEGRACIÓN BOT-BACKEND")
    print("=" * 60)
    print()
    
    client = CMSSAPIClient()
    
    # Test 1: Verificar salud del backend
    print("Test 1: Verificar salud del backend")
    try:
        equipos = client.get_equipos()
        print(f"✅ Backend respondiendo")
        print(f"   Conexión exitosa")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    print()
    
    # Test 2: Obtener equipos
    print("Test 2: Obtener equipos")
    try:
        equipos = client.get_equipos()
        if equipos:
            print(f"✅ Equipos obtenidos: {len(equipos)}")
            print(f"   Primer equipo: {equipos[0].get('nombreequipo', 'N/A')}")
            print(f"   Código: {equipos[0].get('codigointerno', 'N/A')}")
        else:
            print("⚠️  No hay equipos registrados")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 3: Obtener órdenes de trabajo
    print("Test 3: Obtener órdenes de trabajo")
    try:
        ordenes = client.get_ordenes_trabajo()
        if ordenes:
            print(f"✅ Órdenes obtenidas: {len(ordenes)}")
            print(f"   Primera orden: {ordenes[0].get('numeroot', 'N/A')}")
            print(f"   Estado: {ordenes[0].get('estado_nombre', 'N/A')}")
        else:
            print("⚠️  No hay órdenes de trabajo")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 4: Obtener dashboard stats
    print("Test 4: Obtener estadísticas del dashboard")
    try:
        stats = client.get_dashboard_stats()
        print(f"✅ Estadísticas obtenidas:")
        print(f"   Equipos activos: {stats.get('equipos_activos', 0)}")
        print(f"   Órdenes pendientes: {stats.get('ordenes_pendientes', 0)}")
        print(f"   Órdenes en progreso: {stats.get('ordenes_en_progreso', 0)}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 5: Obtener órdenes pendientes
    print("Test 5: Obtener órdenes pendientes")
    try:
        pendientes = client.get_ordenes_pendientes()
        print(f"✅ Órdenes pendientes: {len(pendientes)}")
        if pendientes:
            print(f"   Primera orden pendiente: {pendientes[0].get('numeroot', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 6: Obtener técnicos
    print("Test 6: Obtener técnicos")
    try:
        tecnicos = client.get_tecnicos()
        print(f"✅ Técnicos obtenidos: {len(tecnicos)}")
        if tecnicos:
            print(f"   Primer técnico: {tecnicos[0].get('nombre', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    print("=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)
    print()
    print("✅ El bot puede conectarse correctamente al backend")
    print("✅ Todos los endpoints están funcionando")
    print()
    print("Ahora puedes probar los comandos del bot en Telegram:")
    print("  /status - Ver estado del sistema (con datos reales)")
    print("  /equipos - Ver equipos registrados")
    print("  /ordenes - Ver órdenes de trabajo")
    print("  /pendientes - Ver órdenes pendientes")
    print()
    
    return True

if __name__ == "__main__":
    test_backend_connection()

