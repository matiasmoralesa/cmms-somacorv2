import React, { useState, useEffect } from 'react';
import { X, Save, Calendar, Wrench, Clock, AlertCircle, Package, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { equiposServiceReal } from '@/services/apiServiceReal';
import { planesMantenimientoService } from '@/services/planesMantenimientoService';
import { ordenesTrabajoService } from '@/services/apiService';

interface MaintenancePlan {
  id?: string;
  name: string;
  equipment: string;
  frequency: string;
  description: string;
  estimatedDuration: string;
  active: boolean;
}

interface CreateMaintenancePlanFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  maintenancePlanData?: MaintenancePlan;
}

const CreateMaintenancePlanForm: React.FC<CreateMaintenancePlanFormProps> = ({
  isOpen,
  onClose,
  onSuccess,
  maintenancePlanData
}) => {
  const isEditMode = Boolean(maintenancePlanData);
  const [formData, setFormData] = useState<MaintenancePlan>({
    name: '',
    equipment: '',
    frequency: 'Mensual',
    description: '',
    estimatedDuration: '2 horas',
    active: true
  });
  const [equipos, setEquipos] = useState<Array<{id: number, nombre: string, codigo: string, estado: string}>>([]);
  const [loading, setLoading] = useState(false);
  const [loadingEquipos, setLoadingEquipos] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (maintenancePlanData) {
      setFormData(maintenancePlanData);
    } else {
      setFormData({
        name: '',
        equipment: '',
        frequency: 'Mensual',
        description: '',
        estimatedDuration: '2 horas',
        active: true
      });
    }
  }, [maintenancePlanData, isOpen]);

  useEffect(() => {
    if (isOpen) {
      loadEquipos();
    }
  }, [isOpen]);

  const loadEquipos = async () => {
    try {
      setLoadingEquipos(true);
      setError(null);
      console.log('[PLAN MANTENIMIENTO] Cargando equipos...');
      
      // Verificar si hay token de autenticación
      const token = localStorage.getItem('authToken');
      if (!token) {
        setError('No hay token de autenticación. Por favor, configura el token primero en http://localhost:5173/set_token.html');
        console.error('[PLAN MANTENIMIENTO] No hay token de autenticación');
        return;
      }
      
      const equiposData = await equiposServiceReal.getAll();
      
      // Mapear los datos del backend al formato esperado por el formulario
      const equiposMapeados = (equiposData.results || []).map((eq: any) => ({
        id: eq.idequipo,
        nombre: eq.nombreequipo,
        codigo: eq.codigointerno,
        estado: eq.estado_nombre || 'Desconocido'
      }));
      
      setEquipos(equiposMapeados);
      console.log('[PLAN MANTENIMIENTO] Equipos cargados:', equiposMapeados.length);
    } catch (err: any) {
      console.error('[PLAN MANTENIMIENTO] Error cargando equipos:', err);
      
      // Manejo de errores específicos
      if (err.response?.status === 401) {
        setError('Error de autenticación. Por favor, configura el token de autenticación en http://localhost:5173/set_token.html');
      } else if (err.response?.status === 404) {
        setError('El endpoint de equipos no se encontró. Verifica que el backend esté corriendo.');
      } else if (err.message?.includes('Network Error')) {
        setError('Error de conexión. Verifica que el servidor backend esté corriendo en http://localhost:8000');
      } else {
        setError('Error al cargar los equipos. Por favor, verifica que el servidor esté corriendo.');
      }
    } finally {
      setLoadingEquipos(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validar campos requeridos
      if (!formData.name || !formData.equipment) {
        setError('Por favor completa todos los campos obligatorios');
        setLoading(false);
        return;
      }

      // Obtener el usuario actual del localStorage
      const authData = localStorage.getItem('authToken');
      let userId = 1; // ID por defecto
      
      try {
        if (authData) {
          const userData = JSON.parse(atob(authData.split('.')[1]));
          userId = userData.user_id || 1;
        }
      } catch (e) {
        console.warn('No se pudo obtener el ID del usuario, usando ID por defecto');
      }

      // Generar número de OT único
      const timestamp = Date.now();
      const numeroOT = `OT-PREV-${timestamp}`;

      // Preparar datos para crear una orden de trabajo de tipo preventivo
      const ordenData = {
        numeroot: numeroOT,
        idequipo: parseInt(formData.equipment),
        idsolicitante: userId, // Usuario que crea la orden
        idtipomantenimientoot: 1, // 1 = Preventivo (ajustar según tu BD)
        idestadoot: 1, // 1 = Pendiente (ajustar según tu BD)
        descripcionproblemareportado: formData.name,
        prioridad: 'Media',
        observacionesfinales: `${formData.description}\n\nFrecuencia: ${formData.frequency}\nDuración estimada: ${formData.estimatedDuration}`,
        fechareportefalla: new Date().toISOString()
      };

      console.log('Crear orden de trabajo preventiva:', ordenData);
      
      if (isEditMode && maintenancePlanData?.id) {
        // Actualizar orden existente
        await ordenesTrabajoService.update(parseInt(maintenancePlanData.id), ordenData);
      } else {
        // Crear nueva orden de trabajo
        await ordenesTrabajoService.create(ordenData);
      }
      
      // Mostrar mensaje de éxito
      alert(isEditMode ? 'Plan de mantenimiento actualizado exitosamente' : 'Plan de mantenimiento creado exitosamente');
      
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error al guardar plan de mantenimiento:', err);
      
      // Manejo de errores específicos
      if (err.response?.status === 400) {
        setError('Datos inválidos. Por favor verifica la información ingresada.');
      } else if (err.response?.status === 401) {
        setError('Error de autenticación. Por favor, configura el token de autenticación.');
      } else if (err.response?.status === 404) {
        setError('El endpoint no se encontró. Verifica que el backend esté corriendo.');
      } else if (err.message?.includes('Network Error')) {
        setError('Error de conexión. Verifica que el servidor backend esté corriendo en http://localhost:8000');
      } else {
        setError('Error al guardar el plan de mantenimiento. Por favor intenta nuevamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div>
            <CardTitle className="text-2xl">
              {isEditMode ? 'Editar Plan de Mantenimiento' : 'Nuevo Plan de Mantenimiento'}
            </CardTitle>
            <CardDescription>
              {isEditMode ? 'Modifica los datos del plan de mantenimiento' : 'Crea un nuevo plan de mantenimiento preventivo'}
            </CardDescription>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-destructive" />
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Nombre del Plan *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Ej: Mantenimiento Mensual Bomba"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="equipment">Equipo *</Label>
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
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="frequency">Frecuencia *</Label>
                <Select
                  value={formData.frequency}
                  onValueChange={(value) => setFormData({ ...formData, frequency: value })}
                >
                  <SelectTrigger id="frequency">
                    <SelectValue placeholder="Selecciona frecuencia" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Diaria">Diaria</SelectItem>
                    <SelectItem value="Semanal">Semanal</SelectItem>
                    <SelectItem value="Mensual">Mensual</SelectItem>
                    <SelectItem value="Bimensual">Bimensual</SelectItem>
                    <SelectItem value="Trimestral">Trimestral</SelectItem>
                    <SelectItem value="Semestral">Semestral</SelectItem>
                    <SelectItem value="Anual">Anual</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="estimatedDuration">Duración Estimada *</Label>
                <Select
                  value={formData.estimatedDuration}
                  onValueChange={(value) => setFormData({ ...formData, estimatedDuration: value })}
                >
                  <SelectTrigger id="estimatedDuration">
                    <SelectValue placeholder="Selecciona duración" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="30 minutos">30 minutos</SelectItem>
                    <SelectItem value="1 hora">1 hora</SelectItem>
                    <SelectItem value="2 horas">2 horas</SelectItem>
                    <SelectItem value="3 horas">3 horas</SelectItem>
                    <SelectItem value="4 horas">4 horas</SelectItem>
                    <SelectItem value="1 día">1 día</SelectItem>
                    <SelectItem value="2 días">2 días</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Descripción</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe las tareas y procedimientos del plan de mantenimiento..."
                rows={4}
              />
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="active"
                checked={formData.active}
                onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                className="h-4 w-4 rounded border-gray-300"
              />
              <Label htmlFor="active" className="text-sm font-normal cursor-pointer">
                Plan activo
              </Label>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t">
              <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
                Cancelar
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Guardando...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    {isEditMode ? 'Actualizar' : 'Crear'} Plan
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default CreateMaintenancePlanForm;

