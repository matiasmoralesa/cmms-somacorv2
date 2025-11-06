# Verificación de Conexiones Frontend-Backend

Este documento describe cómo verificar que las conexiones entre el frontend y backend estén funcionando correctamente.

## 📋 Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Verificación Rápida](#verificación-rápida)
- [Verificación Detallada](#verificación-detallada)
- [Interpretación de Resultados](#interpretación-de-resultados)
- [Solución de Problemas](#solución-de-problemas)

## 🔧 Requisitos Previos

Antes de ejecutar las verificaciones, asegúrate de que:

1. **Python 3.8+** esté instalado
2. **Node.js 16+** esté instalado
3. Las dependencias estén instaladas:
   ```bash
   # Backend
   cd somacor_cmms/backend
   pip install -r requirements.txt
   
   # Frontend
   cd somacor_cmms/frontend
   npm install
   ```

## ⚡ Verificación Rápida

### Opción 1: Script Automatizado (Recomendado)

Simplemente ejecuta el script batch:

```bash
cd somacor_cmms
verificar_conexiones.bat
```

Este script:
- ✅ Verifica que el servidor esté corriendo
- ✅ Ejecuta todas las verificaciones automáticamente
- ✅ Genera un reporte completo

### Opción 2: Manual

1. **Inicia el servidor backend:**
   ```bash
   cd somacor_cmms/backend
   python manage.py runserver
   ```

2. **En otra terminal, ejecuta las verificaciones:**
   ```bash
   cd somacor_cmms/backend
   python test_connections.py
   python test_forms_connection.py
   ```

## 🔍 Verificación Detallada

### 1. Verificación de Conexiones Generales

Este script verifica:

- ✅ Conexión al servidor Django
- ✅ Endpoints de la API V1 y V2
- ✅ Configuración CORS
- ✅ Consistencia de datos
- ✅ Endpoints de formularios
- ✅ Funcionalidad de búsqueda
- ✅ Endpoints del dashboard
- ✅ Conectividad del frontend

**Ejecutar:**
```bash
cd somacor_cmms/backend
python test_connections.py
```

### 2. Verificación de Formularios

Este script verifica específicamente:

- ✅ Datos para formulario de equipos
- ✅ Datos para formulario de órdenes de trabajo
- ✅ Datos para formulario de checklist
- ✅ Datos para formulario de usuarios
- ✅ Creación de registros
- ✅ Actualización de registros
- ✅ Validación de formularios
- ✅ Filtros de formularios
- ✅ Búsqueda en formularios

**Ejecutar:**
```bash
cd somacor_cmms/backend
python test_forms_connection.py
```

## 📊 Interpretación de Resultados

### ✅ Significado de los Símbolos

- **✓ Verde**: Prueba exitosa
- **✗ Rojo**: Prueba fallida
- **⚠ Amarillo**: Advertencia (puede requerir atención)

### 📈 Ejemplo de Salida Exitosa

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║          VERIFICACIÓN COMPLETA DE CONEXIONES FRONTEND-BACKEND                ║
║                        Sistema CMMS Somacor                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

================================================================================
                    VERIFICACIÓN DE CONEXIÓN BÁSICA
================================================================================

▶ Conexión al servidor Django... ✓ OK

================================================================================
                    VERIFICACIÓN DE ENDPOINTS DE LA API
================================================================================

▶ API Root... ✓ OK
▶ Faenas... ✓ OK (5 items)
▶ Tipos de Equipo... ✓ OK (8 items)
▶ Estados de Equipo... ✓ OK (4 items)
...

================================================================================
                            REPORTE FINAL
================================================================================

Resumen de Pruebas:
  ✓ Exitosas: 45
  ✗ Fallidas: 0
  ⚠ Advertencias: 2
  Total: 45

Tasa de éxito: 100.0%

✓ ¡Todas las pruebas pasaron exitosamente!
```

## 🔧 Solución de Problemas

### Problema: "No se puede conectar al servidor"

**Solución:**
```bash
# Verifica que el servidor esté corriendo
cd somacor_cmms/backend
python manage.py runserver
```

### Problema: "Endpoint no encontrado (404)"

**Posibles causas:**
1. El endpoint no existe en el backend
2. La URL es incorrecta
3. Las migraciones no se han ejecutado

**Solución:**
```bash
cd somacor_cmms/backend
python manage.py migrate
python manage.py runserver
```

### Problema: "CORS no configurado correctamente"

**Solución:**
Verifica que en `settings.py` esté configurado:
```python
CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
```

### Problema: "No hay datos disponibles"

**Solución:**
```bash
cd somacor_cmms/backend
python manage.py shell
```

En el shell de Django:
```python
from cmms_api.models import *
from django.contrib.auth.models import User

# Crear datos de prueba
# (ver scripts de seed_data.py)
```

### Problema: "Requiere autenticación (401)"

**Solución:**
Los endpoints pueden requerir autenticación. Para desarrollo, puedes:

1. **Crear un superusuario:**
   ```bash
   python manage.py createsuperuser
   ```

2. **Obtener un token:**
   ```bash
   python create_token.py
   ```

3. **Usar el token en las peticiones:**
   ```bash
   curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/equipos/
   ```

## 📝 Verificaciones Adicionales

### Verificar que el Frontend se conecte correctamente

1. **Inicia el frontend:**
   ```bash
   cd somacor_cmms/frontend
   npm run dev
   ```

2. **Abre el navegador:**
   ```
   http://localhost:5173
   ```

3. **Abre la consola del navegador (F12)** y verifica:
   - No hay errores de CORS
   - Las peticiones API se realizan correctamente
   - Los datos se cargan en los formularios

### Verificar Logs del Backend

```bash
cd somacor_cmms/backend
python manage.py runserver --verbosity 2
```

### Verificar Logs del Frontend

En la consola del navegador (F12), busca:
- Errores de red (Network tab)
- Errores de JavaScript (Console tab)
- Errores de React (Console tab)

## 🎯 Checklist de Verificación

Antes de considerar que todo está funcionando correctamente:

- [ ] El servidor backend inicia sin errores
- [ ] El servidor frontend inicia sin errores
- [ ] Todos los endpoints responden correctamente
- [ ] Los datos se cargan en los formularios
- [ ] Se pueden crear nuevos registros
- [ ] Se pueden actualizar registros existentes
- [ ] La validación de formularios funciona
- [ ] Los filtros funcionan correctamente
- [ ] La búsqueda funciona correctamente
- [ ] No hay errores de CORS en la consola del navegador
- [ ] No hay errores de JavaScript en la consola del navegador

## 📞 Soporte

Si encuentras problemas que no se resuelven con este documento:

1. Revisa los logs del servidor
2. Revisa la consola del navegador
3. Verifica que todas las dependencias estén instaladas
4. Verifica que las migraciones se hayan ejecutado
5. Verifica que los puertos 8000 (backend) y 5173 (frontend) estén disponibles

## 🔄 Mantenimiento

Se recomienda ejecutar las verificaciones:

- ✅ Después de actualizar el código
- ✅ Después de instalar nuevas dependencias
- ✅ Después de ejecutar migraciones
- ✅ Antes de hacer un commit importante
- ✅ Después de cambios en la configuración de CORS

## 📚 Referencias

- [Documentación de Django REST Framework](https://www.django-rest-framework.org/)
- [Documentación de React](https://react.dev/)
- [Documentación de Axios](https://axios-http.com/)
- [Documentación de CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

---

**Última actualización:** 2024-11-11  
**Versión:** 1.0.0

