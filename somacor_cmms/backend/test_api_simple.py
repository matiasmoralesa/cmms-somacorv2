import requests

try:
    r = requests.get('http://127.0.0.1:8000/api/v2/equipos/', timeout=5)
    print(f'Status: {r.status_code}')
    print(f'Content-Type: {r.headers.get("Content-Type")}')
    print(f'Data length: {len(r.text)}')
    if r.status_code == 200:
        print('✅ API funcionando correctamente')
    else:
        print(f'❌ Error: {r.status_code}')
except Exception as e:
    print(f'❌ Error de conexión: {e}')
