# ✅ Corrección del Formulario de Plan de Mantenimiento

## 🎯 Problema

El formulario "Nuevo Plan de Mantenimiento" tenía el campo "Equipo" como un input de texto, lo que requería que el usuario escribiera manualmente el nombre del equipo.

## ✅ Solución Implementada

Se modificó el formulario para que el campo "Equipo" sea un **select dropdown** que carga los equipos registrados en el sistema desde el backend.

## 📝 Cambios Realizados

### Archivo: `CreateMaintenancePlanForm.tsx`

#### 1. **Importaciones Agregadas**

```typescript
import { Package } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { equiposServiceReal } from '@/services/apiServiceReal';
```

#### 2. **Estado Agregado**

```typescript
const [equipos, setEquipos] = useState<Array<{
  id: number, 
  nombre: string, 
  codigo: string, 
  estado: string
}>>([]);
const [loadingEquipos, setLoadingEquipos] = useState(false);
```

#### 3. **Función para Cargar Equipos**

```typescript
const loadEquipos = async () => {
  try {
    setLoadingEquipos(true);
    console.log('[PLAN MANTENIMIENTO] Cargando equipos...');
    const equiposData = await equiposServiceReal.getAll();
    
    // Mapear los datos del backend al formato esperado
    const equiposMapeados = (equiposData.results || []).map((eq: any) => ({
      id: eq.idequipo,
      nombre: eq.nombreequipo,
      codigo: eq.codigointerno,
      estado: eq.estado_nombre || 'Desconocido'
    }));
    
    setEquipos(equiposMapeados);
    console.log('[PLAN MANTENIMIENTO] Equipos cargados:', equiposMapeados.length);
  } catch (err) {
    console.error('[PLAN MANTENIMIENTO] Error cargando equipos:', err);
    setError('Error al cargar los equipos. Por favor, verifica que el servidor esté corriendo.');
  } finally {
    setLoadingEquipos(false);
  }
};
```

#### 4. **useEffect para Cargar Equipos**

```typescript
useEffect(() => {
  if (isOpen) {
    loadEquipos();
  }
}, [isOpen]);
```

#### 5. **Campo Convertido de Input a Select**

**Antes:**
```typescript
<Input
  id="equipment"
  value={formData.equipment}
  onChange={(e) => setFormData({ ...formData, equipment: e.target.value })}
  placeholder="Ej: Bomba Centrífuga B-205"
  required
/>
```

**Después:**
```typescript
<Select
  value={formData.equipment}
  onValueChange={(value) => setFormData({ ...formData, equipment: value })}
  disabled={loadingEquipos}
>
  <SelectTrigger id="equipment">
    <SelectValue placeholder={loadingEquipos ? "Cargando equipos..." : "Seleccionar equipo"} />
  </SelectTrigger>
  <SelectContent>
    {equipos.length === 0 && !loadingEquipos ? (
      <div className="p-2 text-sm text-gray-500">
        No hay equipos disponibles
      </div>
    ) : (
      equipos.map((equipo) => (
        <SelectItem key={equipo.id} value={equipo.id.toString()}>
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-2">
              <Package className="h-4 w-4" />
              <span>{equipo.nombre}</span>
            </div>
            <Badge variant="outline" className="ml-2">
              {equipo.codigo}
            </Badge>
          </div>
        </SelectItem>
      ))
    )}
  </SelectContent>
</Select>
{loadingEquipos && (
  <p className="text-xs text-gray-500">Cargando equipos...</p>
)}
```

## 🎨 Características del Nuevo Select

### 1. **Carga Automática de Datos**
- ✅ Los equipos se cargan automáticamente cuando se abre el formulario
- ✅ Conexión directa con el backend
- ✅ Sin datos simulados

### 2. **Interfaz Mejorada**
- ✅ Muestra el nombre del equipo
- ✅ Muestra el código del equipo en un badge
- ✅ Icono de paquete para mejor visualización
- ✅ Placeholder dinámico ("Cargando equipos..." mientras carga)

### 3. **Estados de Carga**
- ✅ Indicador de carga mientras se obtienen los datos
- ✅ Select deshabilitado durante la carga
- ✅ Mensaje si no hay equipos disponibles
- ✅ Manejo de errores con mensaje al usuario

### 4. **Experiencia de Usuario**
- ✅ Búsqueda fácil de equipos
- ✅ Información clara de cada equipo
- ✅ Validación automática
- ✅ Prevención de errores de escritura

## 📊 Ejemplo de Visualización

Cuando el usuario abre el formulario, verá:

```
┌─────────────────────────────────────────┐
│ Equipo *                                │
│ ┌─────────────────────────────────────┐ │
│ │ Seleccionar equipo               ▼ │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘

Al hacer clic, se muestra:

┌─────────────────────────────────────────┐
│ 📦 Excavadora 320D          [EQ001]    │
│ 📦 Bomba Centrífuga B-205   [EQ002]    │
│ 📦 Motor Diesel 500HP       [EQ003]    │
│ 📦 Compresor de Aire        [EQ004]    │
│ ...                                       │
└─────────────────────────────────────────┘
```

## 🔄 Flujo de Funcionamiento

1. **Usuario abre el formulario**
   - Se dispara el `useEffect`
   - Se llama a `loadEquipos()`

2. **Carga de datos**
   - Se hace petición a `equiposServiceReal.getAll()`
   - Se obtienen todos los equipos del backend
   - Se mapean los datos al formato correcto
   - Se actualiza el estado `equipos`

3. **Renderizado del select**
   - Se muestran todos los equipos disponibles
   - Cada equipo muestra nombre y código
   - El usuario puede seleccionar uno

4. **Selección del equipo**
   - El usuario selecciona un equipo
   - Se actualiza `formData.equipment` con el ID del equipo
   - El formulario está listo para enviar

## 🚀 Cómo Probar

### 1. Reinicia el Servidor Backend

```bash
cd somacor_cmms
reiniciar_y_verificar.bat
```

### 2. Inicia el Frontend

```bash
cd somacor_cmms\frontend
npm run dev
```

### 3. Prueba el Formulario

1. Abre `http://localhost:5173`
2. Ve a "Mantenimiento Preventivo"
3. Haz clic en "Nuevo Plan de Mantenimiento"
4. Verifica que el campo "Equipo" sea un select
5. Haz clic en el select
6. Deberías ver todos los equipos registrados

### 4. Verifica en la Consola

Abre la consola del navegador (F12) y deberías ver:

```
[PLAN MANTENIMIENTO] Cargando equipos...
[EQUIPOS] Conectando al backend real...
[EQUIPOS] Datos recibidos del backend: {results: Array(50), ...}
[PLAN MANTENIMIENTO] Equipos cargados: 50
```

## 📝 Ventajas de la Solución

### Antes (Input de texto)
- ❌ Usuario tiene que escribir manualmente
- ❌ Posibles errores de escritura
- ❌ No valida que el equipo exista
- ❌ No muestra información adicional

### Después (Select con datos del backend)
- ✅ Selección fácil y rápida
- ✅ Sin errores de escritura
- ✅ Valida que el equipo exista
- ✅ Muestra código y nombre del equipo
- ✅ Interfaz más profesional
- ✅ Datos siempre actualizados

## 🔧 Troubleshooting

### Problema: "No hay equipos disponibles"

**Causa:** No hay equipos en la base de datos o el backend no está corriendo.

**Solución:**
```bash
# Verificar que el backend esté corriendo
curl http://localhost:8000/api/v2/equipos/

# Si no hay equipos, crear algunos
cd somacor_cmms\backend
python manage.py shell
# Crear equipos en el shell
```

### Problema: "Error al cargar los equipos"

**Causa:** El servidor backend no está corriendo o hay un error de conexión.

**Solución:**
1. Verifica que el servidor esté corriendo
2. Revisa la consola del navegador para ver el error
3. Ejecuta `python test_forms_backend.py` para verificar los endpoints

### Problema: "Cargando equipos..." no desaparece

**Causa:** El backend no responde o hay un error en la petición.

**Solución:**
1. Verifica que el servidor esté corriendo
2. Revisa los logs del backend
3. Verifica que el endpoint `/api/v2/equipos/` funcione

## 📚 Referencias

- [Documentación de React Select](https://www.radix-ui.com/primitives/docs/components/select)
- [Documentación de Axios](https://axios-http.com/)
- [Documentación de React Hooks](https://react.dev/reference/react)

---

**Fecha:** 2024-11-11  
**Versión:** 1.0.0  
**Autor:** Sistema CMMS Somacor  
**Estado:** ✅ Completado

