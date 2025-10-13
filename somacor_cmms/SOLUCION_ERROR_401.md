# 🔧 Solución al Error 401 (Unauthorized)

## 📋 Descripción del Problema

El error **401 Unauthorized** ocurre cuando el frontend intenta acceder a las APIs del backend sin un token de autenticación válido. Este es un problema común que se resuelve fácilmente configurando el token de autenticación.

## ✅ Solución Rápida

### Opción 1: Usar la Página de Configuración (Recomendado)

1. **Inicia los servidores:**
   ```bash
   cd somacor_cmms
   start_optimized_servers.bat
   ```

2. **Espera a que se muestre el token en la consola:**
   ```
   🔑 Token: abc123def456...
   ```

3. **Abre en tu navegador:**
   ```
   http://localhost:5173/set_token.html
   ```

4. **Pega el token** que se mostró en la consola

5. **Haz clic en "Guardar Token"**

6. **¡Listo!** Serás redirigido al sistema

---

### Opción 2: Desde la Consola del Navegador

1. **Inicia los servidores:**
   ```bash
   cd somacor_cmms
   start_optimized_servers.bat
   ```

2. **Copia el token** que se muestra en la consola

3. **Abre tu navegador** en `http://localhost:5173`

4. **Presiona F12** para abrir las herramientas de desarrollador

5. **Ve a la pestaña "Console"**

6. **Ejecuta este comando** (reemplaza `TU_TOKEN` con el token real):
   ```javascript
   localStorage.setItem('authToken', 'TU_TOKEN_AQUI');
   ```

7. **Recarga la página** (F5)

---

### Opción 3: Usar el Script JavaScript

1. **Inicia los servidores:**
   ```bash
   cd somacor_cmms
   start_optimized_servers.bat
   ```

2. **Abre tu navegador** en `http://localhost:5173`

3. **Presiona F12** para abrir las herramientas de desarrollador

4. **Ve a la pestaña "Console"**

5. **Copia y pega el contenido** del archivo `frontend/public/setup_auth.js`

6. **Presiona Enter** y sigue las instrucciones

---

## 🔍 Verificar que el Token Está Configurado

Para verificar que el token se guardó correctamente:

1. Abre la consola del navegador (F12)
2. Ve a la pestaña "Console"
3. Ejecuta:
   ```javascript
   localStorage.getItem('authToken')
   ```
4. Deberías ver tu token

---

## 🔄 Regenerar el Token

Si necesitas regenerar el token:

```bash
cd somacor_cmms/backend
python create_token.py
```

Luego sigue una de las opciones anteriores para configurarlo.

---

## 📝 Notas Importantes

- **El token se guarda en el localStorage del navegador**, por lo que:
  - Si limpias el caché del navegador, perderás el token
  - Si cambias de navegador, necesitarás configurar el token nuevamente
  - El token es específico para cada usuario

- **El token nunca expira** (a menos que lo regeneres manualmente)

- **Si ves el error 401 después de configurar el token:**
  - Verifica que el token se guardó correctamente
  - Asegúrate de que el backend esté corriendo
  - Intenta regenerar el token

---

## 🆘 Problemas Comunes

### Error: "Cannot read property 'authToken' of null"
**Solución:** El localStorage no está disponible. Intenta:
1. Recargar la página
2. Limpiar el caché del navegador
3. Usar un navegador diferente

### Error: "Token inválido"
**Solución:** El token no es válido. Regenera el token:
```bash
cd somacor_cmms/backend
python create_token.py
```

### Error: "Backend no responde"
**Solución:** Verifica que el backend esté corriendo:
1. Abre `http://localhost:8000` en tu navegador
2. Deberías ver la página de Django REST Framework
3. Si no responde, reinicia los servidores

---

## 📞 Soporte

Si después de seguir estos pasos el problema persiste:

1. Verifica los logs del backend: `somacor_cmms/backend/logs/django.log`
2. Verifica la consola del navegador (F12) para ver errores específicos
3. Asegúrate de que estás usando la última versión del código

---

## ✅ Checklist de Verificación

- [ ] El backend está corriendo en `http://localhost:8000`
- [ ] El frontend está corriendo en `http://localhost:5173`
- [ ] El token fue generado correctamente
- [ ] El token fue guardado en localStorage
- [ ] La página fue recargada después de guardar el token
- [ ] No hay errores en la consola del navegador

---

**Última actualización:** 2025-01-10
**Versión:** 1.0.0

