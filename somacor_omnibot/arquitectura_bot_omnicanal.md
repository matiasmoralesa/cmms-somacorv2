# Diseño de la Arquitectura del Bot Omnicanal para Somacor-CMMS

## 1. Introducción

Este documento detalla la arquitectura propuesta para el bot omnicanal de Somacor-CMMS, diseñado para la Etapa 2 del proyecto. El objetivo principal del bot es actuar como una interfaz inteligente entre operarios, técnicos y la administración, facilitando la gestión automatizada de tareas de mantenimiento y mejorando la comunicación a través de múltiples canales, con un enfoque inicial en WhatsApp.

## 2. Componentes Clave de la Arquitectura

La arquitectura del bot omnicanal se basará en los siguientes componentes principales:

### 2.1. Capa de Interfaz de Usuario (Canales)

Esta capa se encargará de la interacción directa con los usuarios a través de diferentes plataformas de mensajería.

*   **WhatsApp**: Integración principal para la comunicación con operarios y técnicos. Se utilizará la API de WhatsApp Business o un proveedor de soluciones de WhatsApp (BSP).
*   **Otros Canales (Futuro)**: Posible expansión a Telegram, Slack, o interfaces web/móviles personalizadas.

### 2.2. Plataforma de Bot (Orquestador)

El corazón del sistema, responsable de recibir mensajes de los canales, procesarlos, interactuar con el motor de IA y el backend del CMMS, y enviar respuestas.

*   **Framework de Bot**: Se podría considerar un framework como [Rasa](https://rasa.com/) (para NLU/NLG y gestión de diálogos) o una solución más ligera basada en Python como [Flask](https://flask.palletsprojects.com/) o [FastAPI](https://fastapi.tiangolo.com/) con librerías específicas para bots.
*   **Gestión de Sesiones**: Mantener el estado de las conversaciones con los usuarios.
*   **Manejo de Eventos**: Procesar eventos entrantes de los canales y salientes hacia el CMMS.

### 2.3. Motor de Inteligencia Artificial (IA)

Encargado de entender la intención del usuario y extraer entidades relevantes de los mensajes.

*   **Procesamiento del Lenguaje Natural (PLN/NLU)**: Identificación de intenciones (ej. "reportar falla", "consultar estado", "agendar mantenimiento") y extracción de entidades (ej. "máquina X", "tipo de falla Y", "fecha Z").
*   **Generación de Lenguaje Natural (GLN/NLG)**: Formulación de respuestas coherentes y contextuales.
*   **Modelos de IA**: Se pueden utilizar modelos pre-entrenados o entrenar modelos personalizados con datos específicos del dominio de mantenimiento de Somacor. Considerar APIs de LLMs como OpenAI (gpt-4.1-mini, gemini-2.5-flash) para capacidades conversacionales avanzadas.

### 2.4. Capa de Integración con CMMS (API)

El puente entre el bot y el sistema CMMS existente, permitiendo al bot acceder y manipular datos del CMMS.

*   **API RESTful**: El backend de Django del CMMS ya expone una API RESTful. El bot interactuará con esta API para:
    *   Consultar información de equipos, órdenes de trabajo, agendas.
    *   Crear/actualizar órdenes de trabajo, reportes de fallas.
    *   Asignar técnicos, registrar mantenimientos.
*   **Autenticación y Autorización**: Asegurar que las interacciones del bot con el CMMS sean seguras y respeten los roles de usuario.

### 2.5. Base de Datos (Existente del CMMS)

El bot utilizará la base de datos existente del CMMS para almacenar y recuperar toda la información relevante de mantenimiento.

*   **SQLite/MySQL**: Según la configuración del CMMS.

## 3. Flujos de Interacción Típicos

### 3.1. Reporte de Falla

1.  **Usuario**: Envía un mensaje al bot (ej. "La máquina excavadora X está fallando, no enciende").
2.  **Capa de Interfaz**: Recibe el mensaje y lo envía a la Plataforma de Bot.
3.  **Plataforma de Bot**: Envía el mensaje al Motor de IA.
4.  **Motor de IA**: Identifica la intención "reportar falla" y extrae entidades ("máquina excavadora X", "no enciende").
5.  **Plataforma de Bot**: Consulta a la Capa de Integración con CMMS para verificar la máquina y obtener información adicional si es necesario.
6.  **Capa de Integración con CMMS**: Interactúa con el backend de Django.
7.  **Plataforma de Bot**: Si la información es suficiente, crea una nueva orden de trabajo o un reporte de falla a través de la API del CMMS. Si falta información, solicita al usuario (ej. "¿Podrías especificar el modelo o número de serie de la excavadora?").
8.  **Plataforma de Bot**: Envía una confirmación al usuario (ej. "Reporte de falla registrado para la excavadora X. Se ha creado la OT #12345.").

### 3.2. Consulta de Estado de Mantenimiento

1.  **Usuario**: Envía un mensaje (ej. "¿Cuál es el estado de la OT #12345?").
2.  **Capa de Interfaz**: Recibe el mensaje.
3.  **Plataforma de Bot**: Envía el mensaje al Motor de IA.
4.  **Motor de IA**: Identifica la intención "consultar estado" y extrae la entidad "OT #12345".
5.  **Plataforma de Bot**: Consulta a la Capa de Integración con CMMS para obtener el estado de la orden de trabajo.
6.  **Capa de Integración con CMMS**: Interactúa con el backend de Django.
7.  **Plataforma de Bot**: Envía el estado al usuario (ej. "La OT #12345 está en estado 'En Progreso', asignada al técnico Juan Pérez.").

## 4. Tecnologías Propuestas

*   **Lenguaje de Programación**: Python (para la Plataforma de Bot y Motor de IA, dada la compatibilidad con el backend de Django y la riqueza de librerías de IA).
*   **Framework de Bot**: [Rasa](https://rasa.com/) (para una solución robusta de IA conversacional) o [Flask/FastAPI](https://flask.palletsprojects.com/) con librerías como `python-telegram-bot` o `twilio` (para WhatsApp) si se prefiere un enfoque más manual.
*   **Integración WhatsApp**: [Twilio API for WhatsApp Business](https://www.twilio.com/whatsapp) o un BSP como [360dialog](https://www.360dialog.com/).
*   **Motor de IA**: Modelos de PLN/NLU/NLG, posiblemente utilizando APIs de LLMs como OpenAI (gpt-4.1-mini, gemini-2.5-flash) para el procesamiento de lenguaje natural y la generación de respuestas.
*   **Base de Datos**: La existente del CMMS (SQLite/MySQL).

## 5. Consideraciones de Seguridad

*   **Autenticación de Usuarios**: Implementar mecanismos seguros para verificar la identidad de los usuarios del bot (ej. integración con el sistema de autenticación del CMMS).
*   **Autorización**: Asegurar que el bot solo realice acciones permitidas para el rol del usuario.
*   **Cifrado de Datos**: Proteger la comunicación entre el bot, los canales y el CMMS.
*   **Validación de Entradas**: Sanitizar y validar todas las entradas de usuario para prevenir ataques de inyección.

## 6. Próximos Pasos

1.  **Selección de Framework/Librerías**: Decidir entre Rasa o un framework más ligero con librerías específicas.
2.  **Configuración de Entorno**: Preparar el entorno de desarrollo para el bot.
3.  **Desarrollo de Integración de Canal**: Implementar la conexión con WhatsApp.
4.  **Desarrollo del Motor de IA**: Entrenar o configurar los modelos de PLN/NLU.
5.  **Desarrollo de Integración con CMMS**: Implementar las llamadas a la API del backend de Django.


