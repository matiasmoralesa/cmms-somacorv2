# Integración del Widget de Chat en el Frontend de Somacor-CMMS

## Descripción General

Se ha implementado un widget de chat flotante en el frontend de Somacor-CMMS que permite a los usuarios interactuar directamente con el bot omnicanal desde la interfaz web. El widget está diseñado con Tailwind CSS y se integra perfectamente con el diseño existente del sistema.

## Características del Widget

### Diseño y UX

- **Botón flotante**: Un botón circular en la esquina inferior derecha que indica la presencia del asistente virtual.
- **Notificación visual**: Indicador de mensajes no leídos con animación de pulso.
- **Ventana de chat**: Interfaz de chat moderna y responsiva con:
  - Header con información del bot y estado en línea
  - Área de mensajes con scroll automático
  - Indicador de escritura cuando el bot está procesando
  - Campo de entrada con soporte para Enter para enviar
  - Botones de minimizar y cerrar

### Funcionalidades

1. **Comunicación en tiempo real**: El widget se comunica con el backend del bot a través de la API expuesta.
2. **Historial de mensajes**: Mantiene el historial de la conversación durante la sesión.
3. **Indicador de estado**: Muestra cuando el bot está escribiendo una respuesta.
4. **Timestamps**: Cada mensaje incluye la hora de envío.
5. **Minimización**: Permite minimizar la ventana de chat sin cerrarla completamente.

## Implementación Técnica

### Archivos Modificados/Creados

1. **`src/components/ChatWidget.tsx`** (Nuevo)
   - Componente principal del widget de chat
   - Maneja el estado de la conversación
   - Gestiona la comunicación con la API del bot

2. **`src/components/layout/AppLayout.tsx`** (Modificado)
   - Se importa y añade el componente `ChatWidget`
   - El widget está disponible en todas las páginas protegidas del sistema

### Integración con el Bot

El widget se comunica con el bot a través de la URL del webhook:

```typescript
const response = await fetch(\'https://5000-iy7mh09a9ivs0xdzc4g3t-a9297ea2.manus.computer/chat\', {
  method: \'POST\',
  headers: {
    \'Content-Type\': \'application/json\',
  },
  body: JSON.stringify({
    message: inputMessage,
    user_id: \'web_user_\', // En producción, usar el ID del usuario autenticado
  }),
});
```

**Nota**: Esta URL es temporal. Para producción, deberás:
1. Desplegar el bot en un servidor permanente
2. Actualizar la URL en el componente `ChatWidget.tsx`
3. Configurar CORS en el backend del bot para permitir peticiones desde el frontend

### Estilos con Tailwind CSS

El widget utiliza clases de Tailwind CSS para:
- Diseño responsivo
- Animaciones suaves
- Gradientes de color
- Sombras y efectos de hover
- Transiciones

## Configuración para Producción

### 1. Actualizar la URL del Bot

En `src/components/ChatWidget.tsx`, línea 46, actualiza la URL:

```typescript
const response = await fetch(\'TU_URL_DE_PRODUCCION/chat\', {
  // ...
});
```

### 2. Configurar CORS en el Backend del Bot

En `somacor_omnibot/app_enhanced.py`, añade soporte para CORS:

```python
from flask import Flask, request
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://tu-dominio-frontend.com"}})

# ... resto del código
```

Instala flask-cors:

```bash
pip install flask-cors
```

### 3. Variables de Entorno

Crea un archivo `.env` en el directorio del frontend con:

```env
VITE_BOT_API_URL=https://tu-servidor-bot.com/chat
```

Y actualiza el componente para usar esta variable:

```typescript
const BOT_API_URL = import.meta.env.VITE_BOT_API_URL || \'http://localhost:5000/chat\';
```

## Pruebas

### Pruebas Locales

1. Asegúrate de que el bot esté ejecutándose:
   ```bash
   cd somacor_omnibot
   source venv/bin/activate
   python app_enhanced.py
   ```

2. Inicia el frontend:
   ```bash
   cd somacor_cmms/frontend
   npm run dev
   ```

3. Accede a `http://localhost:5173` y prueba el widget de chat.

### Comandos de Prueba

Prueba los siguientes mensajes en el chat:
- "hola"
- "reportar falla"
- "estado OT-XXX"
- "equipos"
- "ayuda"

## Mejoras Futuras

1. **Autenticación**: Integrar el sistema de autenticación del CMMS para identificar al usuario en el bot.
2. **Persistencia**: Guardar el historial de conversaciones en la base de datos.
3. **Notificaciones**: Implementar notificaciones push cuando el bot responda.
4. **Adjuntos**: Permitir el envío de imágenes o documentos.
5. **Comandos rápidos**: Añadir botones de acceso rápido para acciones comunes.
6. **Integración profunda con CMMS**: Permitir que el bot realice acciones directamente en el sistema (crear OTs, consultar estados, etc.).

## Soporte

Para cualquier problema o consulta sobre la integración del widget, consulta la documentación principal en `documentacion_bot_omnicanal.md` o contacta al equipo de desarrollo.

