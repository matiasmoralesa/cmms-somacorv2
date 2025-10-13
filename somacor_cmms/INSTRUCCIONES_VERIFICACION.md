# 🔍 Instrucciones de Verificación de Conexiones

## 📋 Resumen

He creado un sistema completo de verificación de conexiones entre el frontend y backend de tu sistema CMMS. Este sistema te permite verificar de manera rápida y completa que todas las conexiones estén funcionando correctamente.

## 🚀 Inicio Rápido

### Opción 1: Verificación Rápida (30 segundos)

```bash
cd somacor_cmms
test_rapido.bat
```

### Opción 2: Verificación Completa (2-3 minutos)

```bash
cd somacor_cmms
verificar_conexiones.bat
```

### Opción 3: Verificación Manual

```bash
# Terminal 1: Iniciar backend
cd somacor_cmms\backend
python manage.py runserver

# Terminal 2: Ejecutar verificaciones
cd somacor_cmms\backend
python test_connections.py
python test_forms_connection.py
```

## 📦 Archivos Creados

### 1. Scripts de Verificación (Python)

#### `backend/test_connections.py`
- **Función:** Verificación completa de conexiones
- **Tiempo:** ~2-3 minutos
- **Pruebas:** 40+ pruebas
- **Incluye:**
  - ✅ Conexión al servidor
  - ✅ Endpoints de API V1 y V2
  - ✅ Configuración CORS
  - ✅ Consistencia de datos
  - ✅ Endpoints de formularios
  - ✅ Búsqueda global
  - ✅ Dashboard
  - ✅ Frontend

#### `backend/test_forms_connection.py`
- **Función:** Verificación específica de formularios
- **Tiempo:** ~1-2 minutos
- **Pruebas:** 20+ pruebas
- **Incluye:**
  - ✅ Datos de formularios
  - ✅ Creación de registros
  - ✅ Actualización de registros
  - ✅ Validación
  - ✅ Filtros
  - ✅ Búsqueda

#### `backend/quick_test.py`
- **Función:** Verificación rápida
- **Tiempo:** ~30 segundos
- **Pruebas:** 6 pruebas esenciales
- **Incluye:**
  - ✅ Conexión al servidor
  - ✅ API básica
  - ✅ Endpoints principales
  - ✅ Dashboard
  - ✅ Frontend

### 2. Scripts Batch (Windows)

#### `verificar_conexiones.bat`
- **Función:** Ejecuta todas las verificaciones automáticamente
- **Incluye:**
  - ✅ Verificación de servidor
  - ✅ Ejecución de tests completos
  - ✅ Generación de reportes

#### `test_rapido.bat`
- **Función:** Ejecuta la verificación rápida
- **Incluye:**
  - ✅ Verificación rápida
  - ✅ Reporte básico

### 3. Documentación

#### `VERIFICACION_CONEXIONES.md`
- **Función:** Documentación completa
- **Incluye:**
  - 📋 Requisitos previos
  - ⚡ Guía de verificación rápida
  - 🔍 Guía de verificación detallada
  - 📊 Interpretación de resultados
  - 🔧 Solución de problemas
  - 🎯 Checklist de verificación

#### `RESUMEN_VERIFICACIONES.md`
- **Función:** Resumen ejecutivo
- **Incluye:**
  - 📦 Lista de archivos creados
  - 🚀 Guía de inicio rápido
  - 📊 Qué verifica cada script
  - 🎨 Características
  - 🔧 Configuración

#### `INSTRUCCIONES_VERIFICACION.md` (este archivo)
- **Función:** Instrucciones rápidas
- **Incluye:**
  - 🚀 Inicio rápido
  - 📦 Descripción de archivos
  - 📊 Interpretación de resultados
  - 🔧 Solución de problemas

## 📊 Interpretación de Resultados

### Símbolos de Estado

- **[OK]**: Prueba exitosa
- **[FAIL]**: Prueba fallida
- **[WARN]**: Advertencia (puede requerir atención)

### Ejemplo de Salida Exitosa

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

### Ejemplo con Advertencias

```
[?] Verificacion Rapida de Conexiones

1. Verificando servidor backend... [WARN] Codigo: 404
2. Verificando API... [OK]
3. Verificando endpoint de faenas... [WARN] Codigo: 401
4. Verificando API V2... [OK]
5. Verificando dashboard... [OK]
6. Verificando frontend... [OK]

[OK] Verificacion rapida completada
```

**Nota:** Las advertencias de código 401 (No autorizado) son normales si no has iniciado sesión.

## 🔧 Solución de Problemas

### Problema: "El servidor no está corriendo"

**Solución:**
```bash
cd somacor_cmms\backend
python manage.py runserver
```

### Problema: "Endpoint no encontrado (404)"

**Solución:**
```bash
cd somacor_cmms\backend
python manage.py migrate
python manage.py runserver
```

### Problema: "No autorizado (401)"

**Solución:**
Esto es normal si no has iniciado sesión. Para desarrollo, puedes:
1. Crear un superusuario: `python manage.py createsuperuser`
2. O usar los datos simulados del frontend

### Problema: "Frontend no está corriendo"

**Solución:**
```bash
cd somacor_cmms\frontend
npm run dev
```

### Problema: "No hay datos disponibles"

**Solución:**
```bash
cd somacor_cmms\backend
python load_sample_data_v2.py
```

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

## 📝 Uso Recomendado

### Después de Actualizar el Código

```bash
cd somacor_cmms
test_rapido.bat
```

### Antes de Hacer un Commit

```bash
cd somacor_cmms
verificar_conexiones.bat
```

### Después de Instalar Dependencias

```bash
cd somacor_cmms
verificar_conexiones.bat
```

### Después de Ejecutar Migraciones

```bash
cd somacor_cmms
verificar_conexiones.bat
```

## 🔄 Mantenimiento

Se recomienda ejecutar las verificaciones:

- ✅ Después de actualizar el código
- ✅ Después de instalar nuevas dependencias
- ✅ Después de ejecutar migraciones
- ✅ Antes de hacer un commit importante
- ✅ Después de cambios en la configuración de CORS
- ✅ Cuando se reporten problemas de conexión

## 📞 Soporte

Si encuentras problemas que no se resuelven con este documento:

1. Revisa los logs del servidor
2. Revisa la consola del navegador (F12)
3. Verifica que todas las dependencias estén instaladas
4. Verifica que las migraciones se hayan ejecutado
5. Consulta la documentación completa: `VERIFICACION_CONEXIONES.md`

## 📚 Recursos Adicionales

- [Documentación Completa](./VERIFICACION_CONEXIONES.md)
- [Resumen Ejecutivo](./RESUMEN_VERIFICACIONES.md)
- [Documentación de Django REST Framework](https://www.django-rest-framework.org/)
- [Documentación de React](https://react.dev/)
- [Documentación de Axios](https://axios-http.com/)

## 🎉 Conclusión

Con estas herramientas, puedes verificar rápidamente que todas las conexiones entre el frontend y backend estén funcionando correctamente. Esto te ayudará a:

- ✅ Detectar problemas tempranamente
- ✅ Ahorrar tiempo en debugging
- ✅ Asegurar la calidad del código
- ✅ Facilitar el desarrollo colaborativo

---

**Creado:** 2024-11-11  
**Versión:** 1.0.0  
**Autor:** Sistema CMMS Somacor

