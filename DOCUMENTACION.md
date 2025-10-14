# Documentación de Cambios y Configuración del Proyecto CMMS Somacor v2

## 1. Resumen de Cambios Realizados

Se han realizado una serie de mejoras y correcciones en la configuración del proyecto para asegurar una correcta integración entre el backend y el frontend, utilizando una base de datos SQLite y preparando el terreno para futuras implementaciones como el bot asistente con Apache Airflow.

### 1.1. Backend (Django)

- **Base de Datos SQLite**: Se ha confirmado y optimizado la configuración para usar SQLite, añadiendo un timeout para evitar bloqueos de la base de datos en desarrollo.
- **Entorno Virtual**: Se ha configurado el proyecto para que se ejecute en un entorno virtual, asegurando un manejo de dependencias limpio y aislado.
- **Dependencias**: Se han añadido las dependencias faltantes (`django-filter`, `channels`, `channels-redis`) al archivo `requirements.txt`.
- **Variables de Entorno**: Se ha creado un archivo `.env` en el backend para gestionar las variables de entorno de forma centralizada.
- **Preparación para Airflow/Dask**: Se ha añadido una sección de configuración en `settings.py` para la futura integración con Apache Airflow y Dask.
- **Script de Inicio**: Se ha creado un script `start_backend.sh` que automatiza la creación del entorno virtual, la instalación de dependencias, la aplicación de migraciones y el inicio del servidor de desarrollo.

### 1.2. Frontend (React + Vite)

- **Variables de Entorno**: Se ha mejorado el archivo `.env` del frontend para incluir la URL de la API, el timeout y otras configuraciones, y se ha actualizado el cliente de API para que las utilice.
- **Cliente de API**: El archivo `apiClient.ts` ahora consume las variables de entorno de Vite (`import.meta.env`), permitiendo una configuración más flexible.
- **Script de Inicio**: Se ha creado un script `start_frontend.sh` que automatiza la instalación de dependencias y el inicio del servidor de desarrollo de Vite.

### 1.3. General

- **Script Maestro**: Se ha creado un script `start_all.sh` en la raíz del proyecto que proporciona instrucciones claras sobre cómo iniciar ambos servicios.

## 2. Cómo Ejecutar el Proyecto

Para facilitar la ejecución del proyecto, se han creado scripts de inicio. Sigue estos pasos:

1.  **Abre dos terminales** en la raíz del proyecto (`/home/ubuntu/cmms-somacorv2`).

2.  **En la primera terminal (Backend)**, ejecuta los siguientes comandos:

    ```bash
    cd somacor_cmms/backend
    ./start_backend.sh
    ```

3.  **En la segunda terminal (Frontend)**, ejecuta los siguientes comandos:

    ```bash
    cd somacor_cmms/frontend
    ./start_frontend.sh
    ```

Una vez iniciados ambos servicios, podrás acceder a la aplicación en `http://localhost:5173`.

## 3. Archivos Modificados y Creados

A continuación se listan los archivos que han sido modificados o creados durante este proceso:

- `/home/ubuntu/cmms-somacorv2/DOCUMENTACION.md` (este archivo)
- `/home/ubuntu/cmms-somacorv2/start_all.sh` (nuevo)
- `/home/ubuntu/cmms-somacorv2/somacor_cmms/backend/.env` (nuevo)
- `/home/ubuntu/cmms-somacorv2/somacor_cmms/backend/start_backend.sh` (nuevo)
- `/home/ubuntu/cmms-somacorv2/somacor_cmms/backend/cmms_project/settings.py` (modificado)
- `/home/ubuntu/cmms-somacorv2/somacor_cmms/backend/requirements.txt` (modificado)
- `/home/ubuntu/cmms-somacorv2/somacor_cmms/frontend/.env` (modificado)
- `/home/ubuntu/cmms-somacorv2/somacor_cmms/frontend/start_frontend.sh` (nuevo)
- `/home/ubuntu/cmms-somacorv2/somacor_cmms/frontend/src/api/apiClient.ts` (modificado)

