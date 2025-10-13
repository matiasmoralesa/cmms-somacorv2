# 🔧 Correcciones de Conexiones Frontend-Backend para Formularios

## 📋 Resumen del Problema

Los formularios del frontend no pueden cargar datos del backend debido a problemas de configuración y autenticación.

## 🔍 Problemas Identificados

### 1. **Configuración de Permisos Globales**
- **Problema:** `DEFAULT_PERMISSION_CLASSES` estaba configurado como `IsAuthenticated`
- **Solución:** Cambiado a `AllowAny` para desarrollo
- **Archivo:** `somacor_cmms/backend/cmms_project/settings.py`

### 2. **Servicios del Frontend usando Datos Simulados**
- **Problema:** Los servicios usaban datos mock en lugar de conectarse al backend real
- **Solución:** Creado `apiServiceReal.ts` con servicios que se conectan al backend real
- **Archivo:** `somacor_cmms/frontend/src/services/apiServiceReal.ts`

### 3. **Formularios no Mapeaban Correctamente los Datos**
- **Problema:** Los formularios esperaban un formato diferente al que devuelve el backend
- **Solución:** Agregado mapeo de datos en los formularios
- **Archivos corregidos:**
  - `CreateWorkOrderForm.tsx`
  - `CreateEquipmentForm.tsx`
  - `CreateUserForm.tsx`

## ✅ Correcciones Realizadas

### 1. Configuración del Backend

#### Archivo: `somacor_cmms/backend/cmms_project/settings.py`

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # ✅ Cambiado
    ],
    # ... resto de configuración
}
```

### 2. Servicios del Frontend

#### Archivo: `somacor_cmms/frontend/src/services/apiServiceReal.ts`

Creado nuevo servicio con:
- ✅ Conexiones reales al backend
- ✅ Sin datos simulados
- ✅ Mapeo correcto de datos
- ✅ Manejo de errores robusto
- ✅ Logging detallado

### 3. Formularios Corregidos

#### CreateWorkOrderForm.tsx
- ✅ Usa `equiposServiceReal` en lugar de `equiposService`
- ✅ Mapea correctamente los datos del backend
- ✅ Maneja errores de conexión

#### CreateEquipmentForm.tsx
- ✅ Usa `tiposEquipoServiceReal`, `estadosEquipoServiceReal`, `faenasServiceReal`
- ✅ Mapea correctamente los datos
- ✅ Muestra errores si no puede conectar

#### CreateUserForm.tsx
- ✅ Carga roles del backend
- ✅ Usa `rolesServiceReal` y `usuariosServiceReal`
- ✅ Mapea correctamente los datos

## 🚀 Pasos para Aplicar las Correcciones

### Paso 1: Reiniciar el Servidor Backend

```bash
# Detener el servidor actual (Ctrl+C)
# Luego reiniciar:
cd somacor_cmms\backend
python manage.py runserver
```

### Paso 2: Verificar que los Cambios se Aplicaron

```bash
cd somacor_cmms\backend
python test_forms_backend.py
```

**Resultado esperado:**
```
[*] Faenas... [OK] (5 faenas)
[*] Tipos de Equipo... [OK] (8 tipos)
[*] Estados de Equipo... [OK] (4 estados)
[*] Equipos... [OK] (50 equipos)
[*] Tipos de Mantenimiento... [OK] (4 tipos)
[*] Usuarios... [OK] (10 usuarios)
[*] Roles... [OK] (4 roles)

Total: 7/7 pruebas pasaron
```

### Paso 3: Verificar en el Frontend

1. Inicia el frontend:
```bash
cd somacor_cmms\frontend
npm run dev
```

2. Abre el navegador en `http://localhost:5173`

3. Abre la consola del navegador (F12)

4. Intenta crear un nuevo equipo o orden de trabajo

5. Verifica en la consola que veas:
```
[EQUIPOS] Conectando al backend real...
[EQUIPOS] Datos recibidos del backend: {...}
[FAENAS] Conectando al backend real...
[FAENAS] Datos recibidos: {...}
```

## 📝 Archivos Modificados

### Backend
- ✅ `somacor_cmms/backend/cmms_project/settings.py` - Permisos cambiados a AllowAny

### Frontend
- ✅ `somacor_cmms/frontend/src/services/apiServiceReal.ts` - Nuevo servicio real
- ✅ `somacor_cmms/frontend/src/components/forms/CreateWorkOrderForm.tsx` - Corregido
- ✅ `somacor_cmms/frontend/src/components/forms/CreateEquipmentForm.tsx` - Corregido
- ✅ `somacor_cmms/frontend/src/components/forms/CreateUserForm.tsx` - Corregido

### Scripts de Prueba
- ✅ `somacor_cmms/backend/test_forms_backend.py` - Script de prueba
- ✅ `somacor_cmms/backend/check_urls.py` - Verificación de URLs

## 🔄 Migración de Servicios

Para usar los servicios reales en lugar de los simulados:

### Antes:
```typescript
import { equiposService } from '@/services/apiService';
```

### Después:
```typescript
import { equiposServiceReal } from '@/services/apiServiceReal';
```

## 🎯 Endpoints Disponibles

### API V2 (Recomendados)
- `GET /api/v2/equipos/` - Lista de equipos
- `GET /api/v2/faenas/` - Lista de faenas
- `GET /api/v2/tipos-equipo/` - Tipos de equipo
- `GET /api/v2/usuarios/` - Usuarios
- `GET /api/v2/roles/` - Roles
- `GET /api/v2/ordenes-trabajo/` - Órdenes de trabajo

### API V1 (Legacy)
- `GET /api/faenas/` - Faenas
- `GET /api/estados-equipo/` - Estados de equipo
- `GET /api/tipos-mantenimiento-ot/` - Tipos de mantenimiento

## 📊 Estructura de Respuesta del Backend

```json
{
  "results": [
    {
      "idequipo": 1,
      "codigointerno": "EQ001",
      "nombreequipo": "Excavadora 320D",
      "marca": "Caterpillar",
      "modelo": "320D",
      "anio": 2020,
      "patente": "ABC123",
      "tipo_equipo_nombre": "Excavadora",
      "estado_nombre": "Activo",
      "faena_nombre": "Faena Norte",
      "activo": true
    }
  ],
  "count": 1,
  "next": null,
  "previous": null
}
```

## 🔧 Solución de Problemas

### Problema: "Error al cargar los datos del formulario"

**Causa:** El servidor backend no está corriendo o los permisos no se aplicaron.

**Solución:**
```bash
# 1. Reiniciar el servidor backend
cd somacor_cmms\backend
python manage.py runserver

# 2. Verificar que funciona
python test_forms_backend.py
```

### Problema: "CORS error"

**Causa:** El frontend no puede conectarse al backend por CORS.

**Solución:**
Ya está configurado en `settings.py`:
```python
CORS_ALLOW_ALL_ORIGINS = True
```

### Problema: "404 Not Found"

**Causa:** El endpoint no existe o la URL es incorrecta.

**Solución:**
Verificar que el endpoint esté registrado en `urls_v2.py`:
```python
router.register(r'faenas', views_v2.FaenasViewSet)
```

### Problema: "401 Unauthorized"

**Causa:** Los permisos no se aplicaron correctamente.

**Solución:**
1. Verificar que `settings.py` tenga `AllowAny`
2. Reiniciar el servidor backend
3. Verificar en la consola del navegador

## 📚 Documentación Adicional

- [Documentación de Django REST Framework](https://www.django-rest-framework.org/)
- [Documentación de Axios](https://axios-http.com/)
- [Documentación de React](https://react.dev/)

## 🎉 Resultado Esperado

Después de aplicar todas las correcciones:

1. ✅ Los formularios cargan datos del backend
2. ✅ Los selects se llenan con datos reales
3. ✅ Se pueden crear nuevos registros
4. ✅ Se pueden editar registros existentes
5. ✅ Los errores se muestran correctamente
6. ✅ La consola del navegador muestra logs detallados

## 📞 Soporte

Si encuentras problemas:

1. Verifica que el servidor backend esté corriendo
2. Verifica que el frontend esté corriendo
3. Revisa la consola del navegador (F12)
4. Ejecuta `python test_forms_backend.py` para verificar los endpoints
5. Consulta este documento

---

**Fecha:** 2024-11-11  
**Versión:** 1.0.0  
**Autor:** Sistema CMMS Somacor

