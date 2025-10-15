# Guía de Uso del Bot de Telegram - Asistente CMMS Somacor

**Bot**: @Somacorbot  
**Estado**: ✅ Activo y funcionando  
**Fecha**: 15 de Octubre de 2025

---

## 🤖 Información del Bot

- **Nombre**: Asistente somacor
- **Username**: @Somacorbot
- **ID**: 8206203157
- **Estado**: Conectado y operativo

---

## 🚀 Cómo Empezar

### 1. Buscar el Bot en Telegram

1. Abre Telegram en tu dispositivo
2. Busca: **@Somacorbot**
3. Haz clic en "Iniciar" o envía `/start`

### 2. Primer Contacto

Cuando envíes `/start`, recibirás un mensaje de bienvenida con información sobre el bot y los comandos disponibles.

---

## 📋 Comandos Disponibles

### Comandos Básicos

#### `/start`
**Descripción**: Mensaje de bienvenida e información inicial  
**Uso**: `/start`  
**Respuesta**: Saludo personalizado y lista de comandos disponibles

#### `/help`
**Descripción**: Ayuda detallada sobre todos los comandos  
**Uso**: `/help`  
**Respuesta**: Lista completa de comandos con descripciones

---

### Comandos de Consulta

#### `/status`
**Descripción**: Estado general del sistema CMMS  
**Uso**: `/status`  
**Respuesta**: 
- Total de equipos activos
- Órdenes de trabajo pendientes
- Órdenes en progreso
- Órdenes completadas hoy
- Estado del sistema

**Ejemplo de respuesta**:
```
📊 ESTADO DEL SISTEMA CMMS

✅ Sistema operativo

📈 Estadísticas:
  • Equipos activos: 150
  • Órdenes pendientes: 12
  • Órdenes en progreso: 8
  • Completadas hoy: 5

Última actualización: 15/10/2025 16:30
```

---

#### `/equipos`
**Descripción**: Lista de equipos registrados en el sistema  
**Uso**: `/equipos` o `/equipos [cantidad]`  
**Parámetros**:
- `cantidad` (opcional): Número de equipos a mostrar (por defecto: 10)

**Ejemplo de respuesta**:
```
🔧 EQUIPOS REGISTRADOS

Total de equipos: 150

📋 Últimos 10 equipos:

1. EQUIPO-001 - Excavadora CAT 320
   Estado: Activo
   Tipo: Equipo Móvil

2. EQUIPO-002 - Camión Volvo FH16
   Estado: Activo
   Tipo: Equipo Móvil

[...]
```

---

#### `/ordenes`
**Descripción**: Últimas órdenes de trabajo  
**Uso**: `/ordenes` o `/ordenes [cantidad]`  
**Parámetros**:
- `cantidad` (opcional): Número de órdenes a mostrar (por defecto: 10)

**Ejemplo de respuesta**:
```
📝 ÓRDENES DE TRABAJO

Total de órdenes: 245

📋 Últimas 10 órdenes:

1. OT-2025-001
   Equipo: EQUIPO-001
   Tipo: Correctivo
   Estado: Completada
   Prioridad: Alta
   Fecha: 15/10/2025

2. OT-2025-002
   Equipo: EQUIPO-005
   Tipo: Preventivo
   Estado: En Progreso
   Prioridad: Media
   Fecha: 15/10/2025

[...]
```

---

#### `/pendientes`
**Descripción**: Órdenes de trabajo pendientes  
**Uso**: `/pendientes`

**Ejemplo de respuesta**:
```
⏳ ÓRDENES PENDIENTES

Total: 12 órdenes

🔴 Alta Prioridad (3):

1. OT-2025-015 - EQUIPO-023
   Tipo: Correctivo
   Reportada: 14/10/2025
   Técnico: Sin asignar

2. OT-2025-018 - EQUIPO-031
   Tipo: Correctivo
   Reportada: 15/10/2025
   Técnico: Juan Pérez

[...]

🟡 Media Prioridad (7):
[...]

🟢 Baja Prioridad (2):
[...]
```

---

#### `/alertas`
**Descripción**: Alertas predictivas de equipos en riesgo  
**Uso**: `/alertas`

**Ejemplo de respuesta**:
```
⚠️ ALERTAS PREDICTIVAS

Equipos en riesgo de falla: 8

🔴 Riesgo Alto (3):

1. EQUIPO-015 - Excavadora CAT 320
   Probabilidad de falla: 95%
   MTBF: 15 días
   Última falla: Hace 14 días
   Acción: Mantenimiento urgente requerido

2. EQUIPO-023 - Camión Volvo FH16
   Probabilidad de falla: 87%
   MTBF: 20 días
   Última falla: Hace 18 días
   Acción: Programar mantenimiento

[...]

🟡 Riesgo Medio (5):
[...]

✅ Se han generado órdenes preventivas automáticamente
```

---

#### `/kpis`
**Descripción**: KPIs principales del sistema de mantenimiento  
**Uso**: `/kpis`

**Ejemplo de respuesta**:
```
📊 KPIs DE MANTENIMIENTO

📈 Indicadores Principales:

⏱️ MTBF (Mean Time Between Failures)
  • Promedio general: 45 días
  • Mejor equipo: 120 días
  • Peor equipo: 8 días

🔧 MTTR (Mean Time To Repair)
  • Promedio general: 4.5 horas
  • Mejor tiempo: 1.2 horas
  • Peor tiempo: 12 horas

✅ Tasa de Completado
  • Órdenes completadas: 85%
  • Órdenes pendientes: 10%
  • Órdenes canceladas: 5%

📅 Mantenimiento Preventivo
  • Cumplimiento: 78%
  • Órdenes programadas: 45
  • Órdenes completadas: 35

🎯 Efectividad General
  • Score de salud promedio: 72/100
  • Equipos críticos: 5
  • Equipos en buen estado: 120

Última actualización: 15/10/2025 16:30
```

---

## 🔔 Notificaciones Automáticas

El bot puede enviar notificaciones automáticas cuando:

### Alertas Predictivas
- Se detecta un equipo con alta probabilidad de falla
- Un equipo supera el umbral de riesgo configurado
- Se genera una orden de trabajo preventiva automática

### Mantenimiento Preventivo
- Se crean nuevas órdenes de mantenimiento preventivo
- Se asignan tareas a técnicos
- Se acerca la fecha de un mantenimiento programado

### Checklists
- Se detectan items críticos fallidos en checklists
- Se generan órdenes correctivas automáticas
- Se identifican patrones de fallas recurrentes

---

## 🔧 Configuración Avanzada

### Obtener tu Chat ID

Para recibir notificaciones personalizadas, necesitas tu Chat ID:

1. Envía cualquier mensaje al bot (por ejemplo: `/start`)
2. Visita esta URL en tu navegador (reemplaza `{TOKEN}` con el token del bot):
   ```
   https://api.telegram.org/bot{TOKEN}/getUpdates
   ```
3. Busca en la respuesta JSON el campo `"chat":{"id":123456789}`
4. Tu Chat ID es el número que aparece después de `"id":`

### Configurar Notificaciones

Para configurar notificaciones automáticas:

1. Obtén tu Chat ID (ver arriba)
2. Edita el archivo `airflow_bot/.env`
3. Agrega tu Chat ID a la variable `TELEGRAM_ADMIN_CHAT_IDS`:
   ```
   TELEGRAM_ADMIN_CHAT_IDS=123456789,987654321
   ```
   (Puedes agregar múltiples IDs separados por comas)
4. Reinicia el sistema

---

## 📱 Uso en Grupos

El bot puede ser agregado a grupos de Telegram para que todo el equipo reciba notificaciones:

1. Agrega @Somacorbot a tu grupo
2. Otorga permisos de administrador (opcional, para mejor funcionalidad)
3. El bot responderá a comandos en el grupo
4. Todos los miembros del grupo verán las notificaciones

---

## 🛠️ Solución de Problemas

### El bot no responde

1. Verifica que el bot esté activo:
   ```bash
   ps aux | grep bot.py
   ```

2. Revisa los logs:
   ```bash
   tail -f /tmp/telegram_bot.log
   ```

3. Reinicia el bot:
   ```bash
   pkill -f bot.py
   cd telegram_integration
   python3.11 bot.py &
   ```

### No recibo notificaciones

1. Verifica que tu Chat ID esté configurado en `.env`
2. Asegúrate de haber iniciado una conversación con el bot (`/start`)
3. Revisa que los DAGs de Airflow estén activos

### El bot responde con errores

1. Verifica que el backend de Django esté corriendo
2. Comprueba la configuración de `CMMS_API_BASE_URL` en `.env`
3. Revisa los logs para ver el error específico

---

## 📊 Estadísticas de Uso

El bot registra automáticamente:
- Comandos ejecutados por usuario
- Horarios de mayor actividad
- Comandos más utilizados
- Tiempo de respuesta promedio

---

## 🔐 Seguridad

### Buenas Prácticas

1. **No compartas el token del bot** - Es como una contraseña
2. **Limita los Chat IDs autorizados** - Solo usuarios de confianza
3. **Revisa los logs regularmente** - Detecta uso no autorizado
4. **Mantén actualizado el sistema** - Aplica parches de seguridad

### Permisos del Bot

El bot tiene los siguientes permisos:
- ✅ Puede unirse a grupos
- ❌ NO puede leer todos los mensajes de grupos (solo comandos)
- ❌ NO soporta inline queries

---

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa esta guía
2. Consulta los logs del bot
3. Revisa la documentación en GitHub
4. Abre un issue en el repositorio

---

## 🎯 Próximas Funcionalidades

Funcionalidades planificadas para futuras versiones:

- [ ] Reportar fallas directamente desde Telegram
- [ ] Consultar historial de un equipo específico
- [ ] Asignar técnicos a órdenes de trabajo
- [ ] Completar órdenes de trabajo
- [ ] Subir fotos de reparaciones
- [ ] Generar reportes en PDF
- [ ] Integración con voz (comandos por audio)
- [ ] Botones interactivos (inline keyboards)

---

**Última actualización**: 15 de Octubre de 2025  
**Versión del bot**: 1.0.0  
**Repositorio**: https://github.com/matiasmoralesa/cmms-somacorv2

