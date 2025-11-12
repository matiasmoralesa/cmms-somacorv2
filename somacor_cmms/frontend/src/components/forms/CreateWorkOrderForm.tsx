import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  X, 
  Plus, 
  AlertTriangle, 
  Clock, 
  CheckCircle,
  Wrench,
  Calendar
} from 'lucide-react';
import { equiposServiceReal, ordenesTrabajoServiceReal, tiposMantenimientoOTServiceReal } from '@/services/apiServiceReal';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface Equipo {
  id: number;
  nombre: string;
  codigo: string;
  estado: string;
}

interface TipoMantenimiento {
  id: number;
  nombre: string;
}

interface WorkOrderFormData {
  equipoId: number;
  tipoMantenimiento: number;
  descripcion: string;
  prioridad: string;
  fechaProgramada: string;
  observaciones: string;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

interface CreateWorkOrderFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function CreateWorkOrderForm({ isOpen, onClose, onSuccess }: CreateWorkOrderFormProps) {
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [tiposMantenimiento, setTiposMantenimiento] = useState<TipoMantenimiento[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<WorkOrderFormData>({
    equipoId: 0,
    tipoMantenimiento: 0,
    descripcion: '',
    prioridad: 'Media',
    fechaProgramada: '',
    observaciones: ''
  });

  // =================================================================================
  // EFECTOS
  // =================================================================================

  useEffect(() => {
    if (isOpen) {
      loadFormData();
    }
  }, [isOpen]);

  // =================================================================================
  // FUNCIONES
  // =================================================================================

  const loadFormData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Cargar equipos del backend
      const equiposData = await equiposServiceReal.getAll();

      // Mapear los datos del backend al formato esperado por el formulario
      const equiposMapeados = (equiposData.results || []).map((eq: any) => ({
        id: eq.idequipo,
        nombre: eq.nombreequipo,
        codigo: eq.codigointerno,
        estado: eq.estado_nombre || 'Desconocido'
      }));

      // Usar tipos de mantenimiento predefinidos ya que el endpoint no existe
      const tiposPredefinidos = [
        { id: 1, nombre: 'Preventivo' },
        { id: 2, nombre: 'Correctivo' },
        { id: 3, nombre: 'Predictivo' },
        { id: 4, nombre: 'Emergencia' }
      ];

      setEquipos(equiposMapeados);
      setTiposMantenimiento(tiposPredefinidos);
    } catch (err) {
      console.error('Error loading form data:', err);
      setError('Error al cargar los datos del formulario');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof WorkOrderFormData, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.equipoId || !formData.tipoMantenimiento || !formData.descripcion) {
      setError('Por favor complete todos los campos obligatorios');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Generar número de OT único basado en timestamp
      const numeroot = `OT-${Date.now()}`;
      
      // Convertir fecha a formato YYYY-MM-DD si existe
      let fechaFormateada = null;
      if (formData.fechaProgramada) {
        const fecha = new Date(formData.fechaProgramada);
        fechaFormateada = fecha.toISOString().split('T')[0]; // Solo la parte de fecha
      }
      
      const workOrderData = {
        numeroot: numeroot,
        idequipo: formData.equipoId,
        idtipomantenimientoot: formData.tipoMantenimiento,
        descripcionproblemareportado: formData.descripcion,
        prioridad: formData.prioridad,
        fechaejecucion: fechaFormateada,
        observacionesfinales: formData.observaciones,
        idsolicitante: 1, // Usuario por defecto (Admin)
        idestadoot: 1 // Estado inicial: Pendiente
      };

      await ordenesTrabajoServiceReal.create(workOrderData);
      
      // Reset form
      setFormData({
        equipoId: 0,
        tipoMantenimiento: 0,
        descripcion: '',
        prioridad: 'Media',
        fechaProgramada: '',
        observaciones: ''
      });

      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error creating work order:', err);
      setError('Error al crear la orden de trabajo');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'Crítica':
        return 'destructive';
      case 'Alta':
        return 'destructive';
      case 'Media':
        return 'default';
      case 'Baja':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'Crítica':
      case 'Alta':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div>
            <CardTitle>Nueva Orden de Trabajo</CardTitle>
            <CardDescription>
              Crear una nueva orden de trabajo de mantenimiento
            </CardDescription>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>

        <CardContent>
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Selección de Equipo */}
            <div className="space-y-2">
              <Label htmlFor="equipo">Equipo *</Label>
              <Select 
                value={formData.equipoId.toString()} 
                onValueChange={(value) => handleInputChange('equipoId', parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar equipo" />
                </SelectTrigger>
                <SelectContent>
                  {equipos.map((equipo) => (
                    <SelectItem key={equipo.id} value={equipo.id.toString()}>
                      <div className="flex items-center justify-between w-full">
                        <span>{equipo.nombre}</span>
                        <Badge variant="outline" className="ml-2">
                          {equipo.codigo}
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Tipo de Mantenimiento */}
            <div className="space-y-2">
              <Label htmlFor="tipoMantenimiento">Tipo de Mantenimiento *</Label>
              <Select 
                value={formData.tipoMantenimiento.toString()} 
                onValueChange={(value) => handleInputChange('tipoMantenimiento', parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar tipo" />
                </SelectTrigger>
                <SelectContent>
                  {tiposMantenimiento.map((tipo) => (
                    <SelectItem key={tipo.id} value={tipo.id.toString()}>
                      <div className="flex items-center gap-2">
                        <Wrench className="h-4 w-4" />
                        {tipo.nombre}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Descripción */}
            <div className="space-y-2">
              <Label htmlFor="descripcion">Descripción del Problema *</Label>
              <Textarea
                id="descripcion"
                placeholder="Describa el problema o trabajo a realizar..."
                value={formData.descripcion}
                onChange={(e) => handleInputChange('descripcion', e.target.value)}
                rows={4}
                required
              />
            </div>

            {/* Prioridad */}
            <div className="space-y-2">
              <Label htmlFor="prioridad">Prioridad</Label>
              <Select 
                value={formData.prioridad} 
                onValueChange={(value) => handleInputChange('prioridad', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar prioridad" />
                </SelectTrigger>
                <SelectContent>
                  {['Baja', 'Media', 'Alta', 'Crítica'].map((prioridad) => (
                    <SelectItem key={prioridad} value={prioridad}>
                      <div className="flex items-center gap-2">
                        {getPriorityIcon(prioridad)}
                        {prioridad}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Fecha Programada */}
            <div className="space-y-2">
              <Label htmlFor="fechaProgramada" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Fecha y Hora Programada
              </Label>
              <Input
                id="fechaProgramada"
                type="datetime-local"
                value={formData.fechaProgramada}
                onChange={(e) => handleInputChange('fechaProgramada', e.target.value)}
                className="w-full"
                placeholder="Seleccione fecha y hora"
              />
              <p className="text-xs text-muted-foreground">
                Seleccione la fecha y hora programada para la ejecución
              </p>
            </div>

            {/* Observaciones */}
            <div className="space-y-2">
              <Label htmlFor="observaciones">Observaciones Adicionales</Label>
              <Textarea
                id="observaciones"
                placeholder="Observaciones adicionales..."
                value={formData.observaciones}
                onChange={(e) => handleInputChange('observaciones', e.target.value)}
                rows={3}
              />
            </div>

            {/* Resumen */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium mb-2">Resumen de la Orden</h4>
              <div className="space-y-1 text-sm text-gray-600">
                <p><strong>Equipo:</strong> {equipos.find(e => e.id === formData.equipoId)?.nombre || 'No seleccionado'}</p>
                <p><strong>Tipo:</strong> {tiposMantenimiento.find(t => t.id === formData.tipoMantenimiento)?.nombre || 'No seleccionado'}</p>
                <p><strong>Prioridad:</strong> 
                  <Badge variant={getPriorityColor(formData.prioridad)} className="ml-2">
                    {getPriorityIcon(formData.prioridad)}
                    <span className="ml-1">{formData.prioridad}</span>
                  </Badge>
                </p>
              </div>
            </div>

            {/* Botones */}
            <div className="flex justify-end gap-3 pt-4">
              <Button type="button" variant="outline" onClick={onClose}>
                Cancelar
              </Button>
              <Button type="submit" disabled={loading} className="bg-primary hover:bg-primary/90">
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Creando...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" />
                    Crear Orden
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
