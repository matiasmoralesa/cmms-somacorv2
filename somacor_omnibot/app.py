from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import requests

app = Flask(__name__)

# Configuración de la API del CMMS
CMMS_API_BASE_URL = os.environ.get('CMMS_API_BASE_URL', 'http://localhost:8000/api/')

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    # Lógica simple para el bot
    if 'hola' in incoming_msg:
        msg.body('¡Hola! Soy el bot de Somacor-CMMS. ¿En qué puedo ayudarte hoy?')
    elif 'estado' in incoming_msg:
        # Aquí se debería integrar con la API del CMMS para obtener el estado
        msg.body('Consultando el estado de tus tareas de mantenimiento...')
        # Ejemplo de llamada a la API (esto es un placeholder, se necesita implementar la lógica real)
        try:
            response = requests.get(f'{CMMS_API_BASE_URL}tasks/')
            if response.status_code == 200:
                tasks = response.json()
                if tasks:
                    msg.body(f'Tienes {len(tasks)} tareas pendientes. La primera es: {tasks[0].get("description")}')
                else:
                    msg.body('No se encontraron tareas pendientes.')
            else:
                msg.body(f'Error al conectar con el CMMS: {response.status_code}')
        except requests.exceptions.ConnectionError:
            msg.body('No se pudo conectar con el servicio CMMS. Por favor, inténtalo más tarde.')

    elif 'reportar falla' in incoming_msg:
        msg.body('Por favor, describe la falla detalladamente, incluyendo el equipo y la naturaleza del problema.')
    else:
        msg.body('No entendí tu mensaje. Puedes decir "hola", "estado" o "reportar falla".')

    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

