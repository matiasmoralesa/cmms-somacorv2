# Guía de Inicio Rápido - Bot Asistente CMMS

Esta guía te ayudará a poner en marcha el Bot Asistente CMMS en menos de 10 minutos.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener:

- ✅ Python 3.11 o superior instalado
- ✅ Git instalado
- ✅ Token de bot de Telegram (obtén uno de [@BotFather](https://t.me/botfather))
- ✅ Acceso al backend de Django del CMMS (URL y token de API)

---

## 🚀 Instalación en 5 Pasos

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/matiasmoralesa/cmms-somacorv2.git
cd cmms-somacorv2
```

### Paso 2: Ejecutar el Script de Instalación

```bash
cd airflow_bot
chmod +x setup.sh
./setup.sh
```

Este script:
- Crea un entorno virtual de Python
- Instala todas las dependencias necesarias
- Configura Apache Airflow
- Crea el usuario administrador de Airflow
- Genera scripts de inicio y detención

### Paso 3: Configurar Variables de Entorno

Edita el archivo `.env` con tus credenciales:

```bash
nano .env
```

**Configuraciones mínimas requeridas**:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38

# API del CMMS
CMMS_API_BASE_URL=http://tu-servidor:8000/api/v2
CMMS_API_TOKEN=tu_token_aqui

# Base de datos (si usas PostgreSQL en producción)
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=cmms_airflow
DATABASE_USER=airflow
DATABASE_PASSWORD=tu_password
```

### Paso 4: Iniciar el Sistema

Desde el directorio raíz del proyecto:

```bash
cd ..
./start_bot_system.sh
```

Este comando iniciará:
1. **Dask Cluster** (procesamiento distribuido)
2. **Apache Airflow** (orquestador de flujos)
3. **Bot de Telegram** (interfaz de usuario)

### Paso 5: Verificar que Todo Funciona

Abre tu navegador y accede a:

- **Airflow UI**: http://localhost:8080
  - Usuario: `admin`
  - Contraseña: `admin123`

- **Dask Dashboard**: http://localhost:8787

En Telegram, busca tu bot y envía el comando `/start`.

---

## 🎯 Primeros Pasos con el Bot

### Comandos Disponibles

Una vez que el bot esté activo, prueba estos comandos en Telegram:

```
/start       - Mensaje de bienvenida
/help        - Ver todos los comandos disponibles
/status      - Estado general del sistema CMMS
/equipos     - Lista de equipos registrados
/ordenes     - Últimas órdenes de trabajo
/pendientes  - Órdenes de trabajo pendientes
/alertas     - Alertas predictivas de fallas
/kpis        - KPIs principales del sistema
```

### Activar los DAGs en Airflow

1. Accede a http://localhost:8080
2. Inicia sesión con `admin` / `admin123`
3. En la lista de DAGs, activa los siguientes:
   - `analisis_predictivo_fallas`
   - `mantenimiento_preventivo_semanal`
   - `procesamiento_checklists_diario`

4. Para ejecutar manualmente un DAG, haz clic en el botón "Play" (▶️) junto al nombre del DAG.

---

## 🔧 Configuración Avanzada

### Configurar Notificaciones de Telegram

Para que el sistema envíe notificaciones automáticas:

1. Obtén tu Chat ID de Telegram:
   - Envía un mensaje a tu bot
   - Visita: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
   - Busca el campo `"chat":{"id":123456789}`

2. Edita el archivo de configuración:
   ```bash
   nano airflow_bot/config/airflow_config.py
   ```

3. Agrega los Chat IDs en la sección correspondiente.

### Entrenar el Modelo de Machine Learning

Si tienes datos históricos suficientes (recomendado: 100+ equipos con historial de fallas):

```bash
source airflow_bot/venv/bin/activate
python ml_models/training/failure_prediction_model.py
```

El modelo entrenado se guardará en `ml_models/models/` y será usado automáticamente por el DAG de análisis predictivo.

---

## 🛑 Detener el Sistema

Para detener todos los servicios:

```bash
./stop_bot_system.sh
```

---

## 📊 Monitoreo y Logs

### Ver Logs de Airflow

```bash
tail -f airflow_bot/logs/scheduler/latest/*.log
```

### Ver Logs del Bot de Telegram

Los logs se muestran en la consola donde ejecutaste `start_bot_system.sh`.

### Dashboard de Dask

Accede a http://localhost:8787 para ver:
- Estado de los workers
- Tareas en ejecución
- Uso de memoria y CPU
- Gráficos de rendimiento

---

## ❓ Solución de Problemas

### El bot no responde en Telegram

1. Verifica que el token sea correcto en `.env`
2. Asegúrate de que el proceso del bot esté corriendo:
   ```bash
   ps aux | grep bot.py
   ```
3. Revisa los logs para ver errores

### Airflow no inicia

1. Verifica que el puerto 8080 no esté en uso:
   ```bash
   lsof -i :8080
   ```
2. Revisa los logs de Airflow:
   ```bash
   cat airflow_bot/logs/scheduler/latest/*.log
   ```

### Los DAGs no se ejecutan

1. Verifica que estén activados (toggle en ON) en la UI de Airflow
2. Revisa que la configuración de la API del CMMS sea correcta
3. Ejecuta manualmente para ver errores en tiempo real

### Error de conexión a la API del CMMS

1. Verifica que `CMMS_API_BASE_URL` sea correcta en `.env`
2. Prueba la conexión:
   ```bash
   curl http://tu-servidor:8000/api/v2/equipos/
   ```
3. Verifica que el token de API sea válido

---

## 📚 Documentación Adicional

- **README Completo**: `airflow_bot/README.md`
- **Reporte de Pruebas**: `REPORTE_PRUEBAS_RENDIMIENTO.md`
- **Video de Referencia**: https://youtu.be/PJzIzytxJ2M
- **Repositorio**: https://github.com/matiasmoralesa/cmms-somacorv2

---

## 🆘 Soporte

Si encuentras problemas o tienes preguntas:

1. Revisa la documentación en el repositorio
2. Consulta el reporte de pruebas para ver ejemplos de uso
3. Abre un issue en GitHub con detalles del problema

---

**¡Listo!** Ya tienes el Bot Asistente CMMS funcionando. 🎉

El sistema comenzará a analizar automáticamente tus datos de mantenimiento y te ayudará a:
- Predecir fallas antes de que ocurran
- Automatizar el mantenimiento preventivo
- Procesar checklists y generar acciones correctivas
- Optimizar la asignación de técnicos
- Mejorar los KPIs de mantenimiento

---

**Última actualización**: 15 de Octubre de 2025

