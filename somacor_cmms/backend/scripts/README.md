# Scripts de Utilidad y Pruebas - CMMS Backend

Este directorio contiene scripts de utilidad, pruebas y generación de datos para el sistema CMMS.

## 📁 Organización

### 🔧 Scripts de Configuración y Administración

- **`create_admin_user.py`** - Crea un usuario administrador para el sistema
- **`create_token.py`** - Genera tokens de autenticación para pruebas
- **`generate_secret_key.py`** - Genera una nueva SECRET_KEY para Django
- **`install_dependencies.py`** - Instala dependencias del proyecto

### 📊 Scripts de Generación de Datos

- **`create_simple_data.py`** - Crea datos básicos de prueba
- **`create_simple_orders.py`** - Crea órdenes de trabajo simples
- **`create_work_orders.py`** - Crea órdenes de trabajo con más detalle
- **`crear_ordenes_2025.py`** - Crea órdenes de trabajo específicas para 2025
- **`generate_data_simple.py`** - Generador simple de datos de prueba
- **`generate_equipos_adicionales.py`** - Genera equipos adicionales
- **`generate_massive_data.py`** - Genera grandes volúmenes de datos de prueba
- **`generate_orders_only.py`** - Genera solo órdenes de trabajo
- **`inject_massive_data.py`** - Inyecta datos masivos en la base de datos
- **`load_sample_data_v2.py`** - Carga datos de ejemplo versión 2
- **`poblar_checklists.py`** - Puebla la base de datos con checklists
- **`populate_test_data.py`** - Puebla datos de prueba completos

### 🔄 Scripts de Ajuste y Corrección

- **`ajustar_caracteristicas_equipos.py`** - Ajusta características de equipos existentes
- **`ajustar_datos_completos.py`** - Ajusta datos completos del sistema
- **`fix_november_data.py`** - Corrige datos específicos de noviembre

### 🗑️ Scripts de Limpieza

- **`reset_database.py`** - Resetea completamente la base de datos
- **`reset_db_simple.py`** - Reseteo simple de la base de datos

### 🧪 Scripts de Prueba y Verificación

#### Pruebas de Conexión
- **`test_connections.py`** - Prueba conexiones básicas
- **`test_connections_enhanced.py`** - Prueba conexiones con más detalle
- **`check_urls.py`** - Verifica URLs del sistema

#### Pruebas de Dashboard
- **`test_dashboard.py`** - Prueba funcionalidad del dashboard
- **`test_dashboard_direct.py`** - Prueba directa del dashboard

#### Pruebas de Formularios
- **`test_forms_backend.py`** - Prueba formularios del backend
- **`test_forms_connection.py`** - Prueba conexión de formularios

#### Pruebas de Login
- **`test_login.py`** - Prueba funcionalidad de login
- **`test_login_complete.py`** - Prueba completa de login

#### Prueba Rápida
- **`quick_test.py`** - Prueba rápida del sistema

### 📋 Scripts de Verificación y Reportes

- **`verificar_equipos_completos.py`** - Verifica integridad de equipos
- **`verificar_metricas_equipos.py`** - Verifica métricas de equipos
- **`verificar_tipos_mantenimiento.py`** - Verifica tipos de mantenimiento
- **`verify_data_2024.py`** - Verifica datos del año 2024
- **`mostrar_equipos_completos.py`** - Muestra equipos completos
- **`resumen_datos_generados.py`** - Genera resumen de datos

## 🚀 Uso Común

### Configuración Inicial

```bash
# 1. Instalar dependencias
python scripts/install_dependencies.py

# 2. Generar SECRET_KEY
python scripts/generate_secret_key.py

# 3. Crear usuario administrador
python scripts/create_admin_user.py

# 4. Cargar datos de prueba
python scripts/load_sample_data_v2.py
```

### Desarrollo y Pruebas

```bash
# Prueba rápida del sistema
python scripts/quick_test.py

# Verificar conexiones
python scripts/test_connections.py

# Probar dashboard
python scripts/test_dashboard.py

# Verificar datos
python scripts/verificar_equipos_completos.py
```

### Generación de Datos

```bash
# Datos simples
python scripts/create_simple_data.py

# Datos masivos
python scripts/generate_massive_data.py

# Órdenes de trabajo para 2025
python scripts/crear_ordenes_2025.py
```

### Limpieza y Reset

```bash
# Reset simple
python scripts/reset_db_simple.py

# Reset completo
python scripts/reset_database.py
```

## ⚠️ Advertencias

- **Scripts de reset**: Eliminarán todos los datos de la base de datos
- **Scripts de generación masiva**: Pueden tardar varios minutos
- **Scripts de prueba**: Algunos requieren que el servidor esté corriendo

## 📝 Notas

- Todos los scripts deben ejecutarse desde el directorio `backend/`
- Asegúrate de tener el entorno virtual activado
- Algunos scripts requieren variables de entorno configuradas

## 🔧 Mantenimiento

**Última actualización:** 11 de noviembre de 2025

**Scripts organizados:** 36 archivos Python movidos desde el directorio raíz

**Optimización:** Parte de la Fase 3 de optimización del backend
