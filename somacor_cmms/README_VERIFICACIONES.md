# 🔍 Sistema de Verificación de Conexiones CMMS

## 📋 Índice

- [Visión General](#visión-general)
- [Características](#características)
- [Instalación Rápida](#instalación-rápida)
- [Uso](#uso)
- [Scripts Disponibles](#scripts-disponibles)
- [Interpretación de Resultados](#interpretación-de-resultados)
- [Troubleshooting](#troubleshooting)
- [Arquitectura](#arquitectura)

## 🎯 Visión General

Sistema completo de verificación de conexiones entre el frontend (React) y backend (Django) del sistema CMMS Somacor. Incluye herramientas para verificar endpoints, formularios, datos, y generar reportes detallados.

## ✨ Características

### 🔧 Verificaciones Automáticas
- ✅ Conexión al servidor Django
- ✅ Endpoints de API V1 y V2
- ✅ Configuración CORS
- ✅ Consistencia de datos
- ✅ Endpoints de formularios
- ✅ Funcionalidad de búsqueda
- ✅ Dashboard
- ✅ Conectividad del frontend

### 📊 Reportes y Logging
- 📝 Logs detallados en archivos
- 📈 Dashboard HTML interactivo
- 📄 Exportación a JSON
- 📊 Estadísticas en tiempo real
- 🔍 Historial de verificaciones

### 🛠️ Herramientas Adicionales
- 🔧 Instalación automática de dependencias
- 🗄️ Verificación de base de datos
- 🔄 Verificación de migraciones
- ⚙️ Configuración de entorno

## 🚀 Instalación Rápida

### Opción 1: Verificación Completa Automática (Recomendada)

```bash
cd somacor_cmms
verificar_sistema_completo.bat
```

Este script ejecuta automáticamente:
1. ✅ Instalación de dependencias
2. ✅ Verificación de conexiones
3. ✅ Verificación de formularios
4. ✅ Generación de reportes

### Opción 2: Verificación Rápida

```bash
cd somacor_cmms
test_rapido.bat
```

### Opción 3: Verificación Manual

```bash
# 1. Instalar dependencias
cd somacor_cmms\backend
python install_dependencies.py

# 2. Verificar conexiones
python test_connections_enhanced.py

# 3. Verificar formularios
python test_forms_connection.py
```

## 📖 Uso

### Verificación Básica

```bash
cd somacor_cmms\backend
python quick_test.py
```

**Salida esperada:**
```
[?] Verificacion Rapida de Conexiones

1. Verificando servidor backend... [OK]
2. Verificando API... [OK]
3. Verificando endpoint de faenas... [OK] (5 faenas)
4. Verificando API V2... [OK]
5. Verificando dashboard... [OK]
6. Verificando frontend... [OK]

[OK] Verificacion rapida completada
```

### Verificación Completa con Reportes

```bash
cd somacor_cmms\backend
python test_connections_enhanced.py
```

**Resultados generados:**
- 📝 `logs/connection_test_YYYYMMDD_HHMMSS.log` - Log detallado
- 📊 `logs/dashboard_YYYYMMDD_HHMMSS.html` - Dashboard HTML
- 📄 `logs/results_YYYYMMDD_HHMMSS.json` - Resultados en JSON

### Instalación de Dependencias

```bash
cd somacor_cmms\backend
python install_dependencies.py
```

**Verificaciones realizadas:**
- ✅ Versión de Python
- ✅ Pip instalado
- ✅ Dependencias requeridas
- ✅ Base de datos
- ✅ Migraciones
- ✅ Archivo .env

## 📦 Scripts Disponibles

### Scripts de Verificación

| Script | Descripción | Tiempo | Pruebas |
|--------|-------------|--------|---------|
| `quick_test.py` | Verificación rápida | ~30s | 6 |
| `test_connections.py` | Verificación completa | ~2-3min | 40+ |
| `test_connections_enhanced.py` | Verificación completa con reportes | ~3-4min | 40+ |
| `test_forms_connection.py` | Verificación de formularios | ~1-2min | 20+ |

### Scripts de Utilidad

| Script | Descripción |
|--------|-------------|
| `install_dependencies.py` | Instala todas las dependencias necesarias |
| `verificar_sistema_completo.bat` | Script automatizado completo |
| `test_rapido.bat` | Verificación rápida (Windows) |
| `verificar_conexiones.bat` | Verificación completa (Windows) |

## 📊 Interpretación de Resultados

### Símbolos de Estado

| Símbolo | Significado | Acción |
|---------|-------------|--------|
| `[OK]` | Prueba exitosa | ✅ Ninguna |
| `[WARN]` | Advertencia | ⚠️ Revisar si es necesario |
| `[FAIL]` | Prueba fallida | ❌ Revisar y corregir |

### Códigos HTTP Comunes

| Código | Significado | Acción |
|--------|-------------|--------|
| 200 | OK | ✅ Funcionando correctamente |
| 401 | No autorizado | ⚠️ Normal si no has iniciado sesión |
| 404 | No encontrado | ❌ Endpoint no existe |
| 500 | Error del servidor | ❌ Revisar logs del servidor |

### Ejemplo de Salida Exitosa

```
================================================================================
                   VERIFICACION COMPLETA DE CONEXIONES FRONTEND-BACKEND
================================================================================

================================================================================
                        VERIFICACION DE CONEXION BASICA
================================================================================

[*] Conexion al servidor Django... [OK]

================================================================================
                    VERIFICACION DE ENDPOINTS DE LA API
================================================================================

[*] API Root... [OK]
[*] Faenas... [OK] (5 items)
[*] Tipos de Equipo... [OK] (8 items)
[*] Estados de Equipo... [OK] (4 items)
[*] Roles... [OK] (4 items)
[*] Equipos V2... [OK] (50 items)
[*] Ordenes de Trabajo V2... [OK] (100 items)
[*] Dashboard Stats V2... [OK]
[*] Dashboard Monthly Data V2... [OK]
[*] Dashboard Maintenance Types V2... [OK]
[*] Usuarios V2... [OK] (10 items)
[*] Faenas V2... [OK] (5 items)
[*] Tipos de Equipo V2... [OK] (8 items)

================================================================================
                            REPORTE FINAL
================================================================================

Resumen de Pruebas:
  [OK] Exitosas: 45
  [FAIL] Fallidas: 0
  [WARN] Advertencias: 2
  Total: 45

Tasa de exito: 100.0%

[OK] Todas las pruebas pasaron exitosamente!
```

## 🔧 Troubleshooting

### Problema: "No se puede conectar al servidor"

**Síntomas:**
```
[FAIL] No se puede conectar al servidor. ¿Esta corriendo en http://localhost:8000?
```

**Solución:**
```bash
cd somacor_cmms\backend
python manage.py runserver
```

### Problema: "Endpoint no encontrado (404)"

**Síntomas:**
```
[FAIL] Endpoint no encontrado
```

**Solución:**
```bash
cd somacor_cmms\backend
python manage.py migrate
python manage.py runserver
```

### Problema: "No autorizado (401)"

**Síntomas:**
```
[WARN] Requiere autenticacion (esperado)
```

**Explicación:**
Esto es normal si no has iniciado sesión. Los endpoints protegidos requieren autenticación.

**Solución (opcional):**
```bash
cd somacor_cmms\backend
python manage.py createsuperuser
```

### Problema: "No hay datos disponibles"

**Síntomas:**
```
[WARN] No hay datos de Faenas
```

**Solución:**
```bash
cd somacor_cmms\backend
python load_sample_data_v2.py
```

### Problema: "Dependencias no instaladas"

**Síntomas:**
```
[ERROR] No module named 'requests'
```

**Solución:**
```bash
cd somacor_cmms\backend
python install_dependencies.py
```

## 🏗️ Arquitectura

### Estructura de Archivos

```
somacor_cmms/
├── backend/
│   ├── test_connections.py              # Verificación básica
│   ├── test_connections_enhanced.py     # Verificación con reportes
│   ├── test_forms_connection.py         # Verificación de formularios
│   ├── quick_test.py                    # Verificación rápida
│   ├── install_dependencies.py          # Instalador de dependencias
│   ├── logs/                            # Directorio de logs
│   │   ├── connection_test_*.log        # Logs de verificaciones
│   │   ├── dashboard_*.html             # Dashboards HTML
│   │   └── results_*.json               # Resultados JSON
│   └── ...
├── verificar_sistema_completo.bat       # Script automatizado
├── test_rapido.bat                      # Verificación rápida
├── verificar_conexiones.bat             # Verificación completa
└── README_VERIFICACIONES.md             # Este archivo
```

### Flujo de Verificación

```
┌─────────────────────────────────────────────────────────────┐
│                    VERIFICACION COMPLETA                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │  1. Verificar Conexión Básica         │
        │     - Servidor Django                 │
        │     - API Root                        │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │  2. Verificar Endpoints API           │
        │     - API V1                          │
        │     - API V2                          │
        │     - Dashboard                       │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │  3. Verificar Configuración CORS      │
        │     - Headers CORS                    │
        │     - Orígenes permitidos             │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │  4. Verificar Consistencia de Datos   │
        │     - Faenas                          │
        │     - Tipos de Equipo                 │
        │     - Estados de Equipo               │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │  5. Verificar Formularios             │
        │     - Datos de formularios            │
        │     - Creación de registros           │
        │     - Actualización de registros      │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │  6. Generar Reportes                  │
        │     - Logs detallados                 │
        │     - Dashboard HTML                  │
        │     - Resultados JSON                 │
        └───────────────────────────────────────┘
```

## 📚 Recursos Adicionales

- [Documentación Completa](./VERIFICACION_CONEXIONES.md)
- [Instrucciones Rápidas](./INSTRUCCIONES_VERIFICACION.md)
- [Resumen Ejecutivo](./RESUMEN_VERIFICACIONES.md)
- [Documentación de Django REST Framework](https://www.django-rest-framework.org/)
- [Documentación de React](https://react.dev/)
- [Documentación de Axios](https://axios-http.com/)

## 🤝 Contribuciones

Si encuentras problemas o tienes sugerencias de mejora:

1. Revisa la sección de Troubleshooting
2. Consulta los logs en `somacor_cmms/backend/logs/`
3. Verifica la documentación completa
4. Reporta el problema con los logs correspondientes

## 📝 Notas

- Las verificaciones son no destructivas
- Los logs se guardan automáticamente
- Los reportes HTML son interactivos
- El sistema es compatible con Windows, Linux y macOS

## 📄 Licencia

Sistema CMMS Somacor - Todos los derechos reservados

---

**Versión:** 2.0.0  
**Última actualización:** 2024-11-11  
**Autor:** Sistema CMMS Somacor

