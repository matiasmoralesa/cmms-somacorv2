#!/usr/bin/env python
"""
Script de prueba para verificar los endpoints del dashboard
"""
import requests
import json

BASE_URL = "http://localhost:8000"
TOKEN = "806c849de0c1e165d3bc268f96224ffd94e2a2b8"  # Token del admin

def test_endpoint(endpoint, name):
    """Probar un endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"\n{'='*60}")
    print(f"🔵 Probando: {name}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, allow_redirects=False)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta exitosa")
            print(f"Datos: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Probar endpoints del dashboard
    test_endpoint("/api/v2/dashboard/stats/", "Dashboard Stats")
    test_endpoint("/api/v2/dashboard/monthly_data/", "Monthly Data")
    test_endpoint("/api/v2/dashboard/recent_work_orders/", "Recent Work Orders")
    test_endpoint("/api/v2/dashboard/maintenance_types/", "Maintenance Types")
