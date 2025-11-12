import requests

# Primero hacer login
login_response = requests.post(
    'http://localhost:8000/api/login/',
    json={'username': 'admin', 'password': 'admin123'}
)

if login_response.status_code == 200:
    token = login_response.json()['token']
    print(f"✅ Login exitoso. Token: {token[:20]}...")
    
    # Obtener equipos
    equipos_response = requests.get(
        'http://localhost:8000/api/v2/equipos/',
        headers={'Authorization': f'Token {token}'}
    )
    
    if equipos_response.status_code == 200:
        equipos = equipos_response.json()
        if 'results' in equipos:
            equipos = equipos['results']
        
        if equipos:
            primer_equipo = equipos[0]
            print(f"✅ Equipos obtenidos. Primer equipo: {primer_equipo['nombreequipo']} (ID: {primer_equipo['idequipo']})")
            
            # Obtener template de checklist para el primer equipo
            checklist_response = requests.get(
                f"http://localhost:8000/api/v2/checklist-workflow/templates-por-equipo/{primer_equipo['idequipo']}/",
                headers={'Authorization': f'Token {token}'}
            )
            
            print(f"\n📋 Respuesta del endpoint de checklist:")
            print(f"   Status: {checklist_response.status_code}")
            
            if checklist_response.status_code == 200:
                data = checklist_response.json()
                print(f"   ✅ Templates encontrados: {len(data.get('templates', []))}")
                if data.get('templates'):
                    template = data['templates'][0]
                    print(f"   📝 Template: {template['nombre']}")
                    print(f"   📂 Categorías: {len(template.get('categories', []))}")
                else:
                    print(f"   ⚠️  No hay templates para este equipo")
            else:
                print(f"   ❌ Error: {checklist_response.text}")
        else:
            print("❌ No hay equipos en la base de datos")
    else:
        print(f"❌ Error al obtener equipos: {equipos_response.status_code}")
else:
    print(f"❌ Error en login: {login_response.status_code}")
