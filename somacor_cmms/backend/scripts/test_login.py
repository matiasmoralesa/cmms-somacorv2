#!/usr/bin/env python
"""
Script de prueba para verificar el login directamente
"""
import requests
import json

# URL del backend
BASE_URL = "http://localhost:8000"

def test_login():
    """Probar el endpoint de login"""
    url = f"{BASE_URL}/api/login/"
    
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🔵 Probando login en: {url}")
    print(f"📦 Datos: {json.dumps(data, indent=2)}")
    
    try:
        # Forzar HTTP y deshabilitar redirects
        response = requests.post(url, json=data, headers=headers, allow_redirects=False, verify=False)
        
        print(f"\n📊 Respuesta:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"\n✅ Login exitoso!")
            print(f"Respuesta: {json.dumps(response.json(), indent=2)}")
        elif response.status_code == 301 or response.status_code == 302:
            print(f"\n⚠️ Redirect detectado!")
            print(f"Location: {response.headers.get('Location', 'N/A')}")
        else:
            print(f"\n❌ Error en login")
            print(f"Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Error de conexión: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_login()
