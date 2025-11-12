# Vistas a Conectar al Backend

## Estado Actual (Después de Limpiar BD)

Ahora que la base de datos está limpia (solo usuarios), estas vistas deben mostrar:
- **Estado vacío** cuando no hay datos
- **Mensaje claro** indicando que no hay registros
- **Botón para crear** el primer registro
- **Datos reales** del backend cuando existan

## Vistas Identificadas

### 1. ✅ Dashboard - YA CONECTADO
- Muestra datos reales de órdenes y equipos
- Calcula tendencias dinámicas

### 2. ✅ Equipos - YA CONECTADO  
- Lista equipos desde el backend
- Botones funcionales (ver, editar, eliminar)

### 3. ✅ Órdenes de Trabajo - YA CONECTADO
- Carga órdenes reales
- Filtros y búsqueda funcionales

### 4. ✅ Mantenimiento Preventivo - YA CONECTADO
- Usa órdenes de trabajo preventivas
- Estadísticas calculadas en tiempo real

### 5. ⚠️ Tipos de Tarea - VERIFICAR
- Debe cargar desde `/api/v2/tipos-tarea/`
- Mostrar estado vacío si no hay datos

### 6. ⚠️ Tipos de Equipo - VERIFICAR
- Debe cargar desde `/api/v2/tipos-equipo/`
- Mostrar estado vacío si no hay datos

### 7. ⚠️ Faenas - VERIFICAR
- Debe cargar desde `/api/v2/faenas/`
- Mostrar estado vacío si no hay datos

### 8. ⚠️ Perfiles/Usuarios - VERIFICAR
- Debe cargar desde `/api/v2/usuarios/`
- Mostrar usuarios reales

### 9. ⚠️ Mantenimiento No Planificado - VERIFICAR
- Debe cargar órdenes correctivas
- Mostrar estado vacío si no hay datos

### 10. ⚠️ Calendario - VERIFICAR
- Debe cargar eventos desde `/api/v2/agendas/`
- Mostrar calendario vacío si no hay eventos

### 11. ⚠️ Técnicos - VERIFICAR
- Debe cargar usuarios con rol técnico
- Mostrar estado vacío si no hay técnicos

### 12. ⚠️ Inventario - VERIFICAR
- Debe cargar desde `/api/v2/inventario/`
- Mostrar estado vacío si no hay items

## Próximos Pasos

1. Verificar cada vista marcada con ⚠️
2. Asegurar que muestren estado vacío apropiado
3. Conectar al backend si no lo están
4. Probar creación de primer registro
