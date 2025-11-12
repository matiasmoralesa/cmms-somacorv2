# Solución Error HTTPS/HSTS - Equipos Móviles

**Fecha:** 11 de noviembre de 2025  
**Error:** "You're accessing the development server over HTTPS, but it only supports HTTP"

---

## 🐛 Problema

El navegador está forzando HTTPS debido a caché de HSTS (HTTP Strict Transport Security), pero el servidor de desarrollo Django solo soporta HTTP.

**Síntomas:**
- Error "No 'Access-Control-Allow-Origin' header"
- API devuelve HTML en lugar de JSON
- Errores 404 en endpoints
- Consola muestra errores de HTTPS

---

## ✅ Solución Rápida

### Opción 1: Limpiar Caché de HSTS en Chrome/Edge

1. **Abrir la página de configuración de HSTS:**
   - Chrome: `chrome://net-internals/#hsts`
   - Edge: `edge://net-internals/#hsts`

2. **En la sección "Delete domain security policies":**
   - Escribir: `localhost`
   - Click en "Delete"
   - Escribir: `127.0.0.1`
   - Click en "Delete"

3. **Cerrar y reabrir el navegador**

4. **Limpiar caché del navegador:**
   - Presionar `Ctrl + Shift + Delete`
   - Seleccionar "Cached images and files"
   - Click en "Clear data"

5. **Recargar la página:** `Ctrl + F5` (recarga forzada)

---

### Opción 2: Usar Modo Incógnito

1. Abrir una ventana de incógnito: `Ctrl + Shift + N`
2. Navegar a `http://localhost:5173`
3. El modo incógnito no tiene caché de HSTS

---

### Opción 3: Usar Firefox (Recomendado para Desarrollo)

Firefox maneja HSTS de forma diferente y es más fácil de limpiar:

1. Abrir Firefox
2. Navegar a `http://localhost:5173`
3. Si hay problema, ir a `about:preferences#privacy`
4. Click en "Clear Data"
5. Seleccionar "Cookies and Site Data"
6. Click en "Clear"

---

### Opción 4: Cambiar Puerto del Frontend

Si el problema persiste, cambiar el puerto del frontend:

```bash
# En somacor_cmms/frontend/package.json
"scripts": {
  "dev": "vite --port 3000"  # Cambiar de 5173 a 3000
}
```

Luego actualizar CORS en backend:
```python
# backend/cmms_project/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

---

## 🔧 Verificación

### 1. Verificar que el backend use HTTP

```bash
# Debe mostrar http:// no https://
python manage.py runserver
# Output: Starting development server at http://127.0.0.1:8000/
```

### 2. Verificar configuración del frontend

```bash
# En somacor_cmms/frontend/.env
cat .env
# Debe mostrar: VITE_API_BASE_URL=http://localhost:8000/api/
```

### 3. Probar endpoint directamente

Abrir en el navegador (modo incógnito):
```
http://localhost:8000/api/v2/equipos/
```

Debe mostrar JSON, no error de HTTPS.

---

## 🎯 Solución Definitiva Aplicada

### 1. Limpiar HSTS del Navegador

**Chrome/Edge:**
1. Ir a `chrome://net-internals/#hsts`
2. Eliminar `localhost` y `127.0.0.1`
3. Reiniciar navegador

**Firefox:**
1. Ir a `about:preferences#privacy`
2. Clear Data → Cookies and Site Data
3. Reiniciar navegador

### 2. Forzar Recarga Sin Caché

```
Ctrl + Shift + Delete (limpiar caché)
Ctrl + F5 (recarga forzada)
```

### 3. Verificar en Consola del Navegador

Debe mostrar:
```
🔵 [API] GET /api/v2/equipos/
✅ [API] GET /api/v2/equipos/ - Status: 200
```

No debe mostrar errores de CORS o HTTPS.

---

## 📝 Prevención Futura

### En Desarrollo

**Nunca usar HTTPS en desarrollo local:**
```python
# settings.py - Desarrollo
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
```

**Siempre usar HTTP en URLs:**
```typescript
// .env
VITE_API_BASE_URL=http://localhost:8000/api/  # HTTP, no HTTPS
```

### En Producción

**Usar HTTPS solo en producción:**
```python
# settings.py - Producción
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## ✅ Resultado Esperado

Después de aplicar la solución:

1. ✅ Backend responde en HTTP sin errores
2. ✅ Frontend se conecta correctamente
3. ✅ Equipos Móviles carga datos
4. ✅ Sin errores de CORS
5. ✅ Sin errores de HTTPS

**La vista de Equipos Móviles debe cargar correctamente con los datos.**

---

**Solución creada:** 11 de noviembre de 2025  
**Estado:** ✅ DOCUMENTADO  
**Acción requerida:** Limpiar HSTS del navegador
