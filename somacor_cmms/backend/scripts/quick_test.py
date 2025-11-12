#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba rápida de conexiones
Verifica rápidamente que el sistema esté funcionando
"""

import requests
import sys
import os

# Configurar encoding para Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')

def test_quick():
    """Prueba rápida de conexiones"""
    print("\n[?] Verificacion Rapida de Conexiones\n")
    
    # Test 1: Servidor backend
    print("1. Verificando servidor backend...", end=" ")
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            print("[OK]")
        else:
            print(f"[WARN] Codigo: {response.status_code}")
    except:
        print("[FAIL] - El servidor no esta corriendo")
        print("   Ejecuta: python manage.py runserver")
        return False
    
    # Test 2: API Root
    print("2. Verificando API...", end=" ")
    try:
        response = requests.get("http://localhost:8000/api/", timeout=5)
        if response.status_code in [200, 401]:
            print("[OK]")
        else:
            print(f"[WARN] Codigo: {response.status_code}")
    except:
        print("[FAIL]")
        return False
    
    # Test 3: Endpoint de faenas
    print("3. Verificando endpoint de faenas...", end=" ")
    try:
        response = requests.get("http://localhost:8000/api/faenas/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                print(f"[OK] ({len(data['results'])} faenas)")
            else:
                print("[OK]")
        else:
            print(f"[WARN] Codigo: {response.status_code}")
    except:
        print("[FAIL]")
        return False
    
    # Test 4: API V2
    print("4. Verificando API V2...", end=" ")
    try:
        response = requests.get("http://localhost:8000/api/v2/equipos/", timeout=5)
        if response.status_code in [200, 401]:
            print("[OK]")
        else:
            print(f"[WARN] Codigo: {response.status_code}")
    except:
        print("[FAIL]")
        return False
    
    # Test 5: Dashboard
    print("5. Verificando dashboard...", end=" ")
    try:
        response = requests.get("http://localhost:8000/api/v2/dashboard/stats/", timeout=5)
        if response.status_code in [200, 401]:
            print("[OK]")
        else:
            print(f"[WARN] Codigo: {response.status_code}")
    except:
        print("[FAIL]")
        return False
    
    # Test 6: Frontend
    print("6. Verificando frontend...", end=" ")
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print("[OK]")
        else:
            print(f"[WARN] Codigo: {response.status_code}")
    except:
        print("[WARN] Frontend no esta corriendo (opcional)")
    
    print("\n[OK] Verificacion rapida completada\n")
    return True

if __name__ == "__main__":
    try:
        success = test_quick()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Verificacion interrumpida\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}\n")
        sys.exit(1)

