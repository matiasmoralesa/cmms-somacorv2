import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  X, 
  Plus, 
  Wrench,
  MapPin,
  Tag
} from 'lucide-react';
import { equiposServiceReal, tiposEquipoServiceReal, estadosEquipoServiceReal, faenasServiceReal } from '@/services/apiServiceReal';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface TipoEquipo {
  id: number;
  nombre: string;
}

interface EstadoEquipo {
  id: number;
  nombre: string;
}

interface Faena {
  id: number;
  nombre: string;
  activa: boolean;
}

interface EquipmentFormData {
  codigo: string;
  nombre: string;
  marca: string;
  modelo: string;
  anio: number;
  patente: string;
  tipoEquipo: number;
  estadoEquipo: number;
  faena: number;
  activo: boolean;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

interface CreateEquipmentFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  equipmentData?: any;
}

export default function CreateEquipmentForm({ isOpen, onClose, onSuccess, equipmentData }: CreateEquipmentFormProps) {
  const isEditMode = Boolean(equipmentData);
  const [tiposEquipo, setTiposEquipo] = useState<TipoEquipo[]>([]);
  const [estadosEquipo, setEstadosEquipo] = useState<EstadoEquipo[]>([]);
  const [faenas, setFaenas] = useState<Faena[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<EquipmentFormData>({
    codigo: '',
    nombre: '',
    marca: '',
    modelo: '',
    anio: new Date().getFullYear(),
    patente: '',
    tipoEquipo: 0,
    estadoEquipo: 0,
    faena: 0,
    activo: true
  });

  // =================================================================================
  // EFECTOS
  // =================================================================================

  useEffect(() => {
    if (isOpen) {
      loadFormData();
      if (equipmentData) {
        // Cargar datos del equipo para edición
        setFormData({
          codigo: equipmentData.codigo || '',
          nombre: equipmentData.nombre || '',
          marca: equipmentData.marca || '',
          modelo: equipmentData.modelo || '',
          anio: equipmentData.anio || new Date().getFullYear(),
          patente: equipmentData.patente || '',
          tipoEquipo: equipmentData.tipoEquipo || 0,
          estadoEquipo: equipmentData.estadoEquipo || 0,
          faena: equipmentData.faena || 0,
          activo: equipmentData.activo !== undefined ? equipmentData.activo : true
        });
      } else {
        // Reset form for new equipment
        setFormData({
          codigo: '',
          nombre: '',
          marca: '',
          modelo: '',
          anio: new Date().getFullYear(),
          patente: '',
          tipoEquipo: 0,
          estadoEquipo: 0,
          faena: 0,
          activo: true
        });
      }
    }
  }, [isOpen, equipmentData]);

  // =================================================================================
  // FUNCIONES
  // =================================================================================

  const loadFormData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [tiposData, estadosData, faenasData] = await Promise.all([
        tiposEquipoServiceReal.getAll(),
        estadosEquipoServiceReal.getAll(),
        faenasServiceReal.getAll()
      ]);

      // Mapear los datos del backend al formato esperado por el formulario
      const tiposMapeados = (tiposData.results || []).map((tipo: any) => ({
        id: tipo.idtipoequipo,
        nombre: tipo.nombretipo
      }));

      const estadosMapeados = (estadosData.results || []).map((estado: any) => ({
        id: estado.idestadoequipo,
        nombre: estado.nombreestado
      }));

      const faenasMapeadas = (faenasData.results || []).map((faena: any) => ({
        id: faena.idfaena,
        nombre: faena.nombrefaena,
        activa: faena.activa
      }));

      setTiposEquipo(tiposMapeados);
      setEstadosEquipo(estadosMapeados);
      setFaenas(faenasMapeadas);
    } catch (err: any) {
      console.error('Error loading form data:', err);
      setError('Error al cargar los datos del formulario. Por favor, verifica que el servidor esté corriendo.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof EquipmentFormData, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.codigo || !formData.nombre || !formData.tipoEquipo || !formData.estadoEquipo) {
      setError('Por favor complete todos los campos obligatorios');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const equipmentData = {
        codigointerno: formData.codigo,
        nombreequipo: formData.nombre,
        marca: formData.marca,
        modelo: formData.modelo,
        anio: formData.anio,
        patente: formData.patente,
        idtipoequipo: formData.tipoEquipo,
        idestadoactual: formData.estadoEquipo,
        idfaenaactual: formData.faena || null,
        activo: formData.activo
      };

      await equiposServiceReal.create(equipmentData);
      
      // Reset form
      setFormData({
        codigo: '',
        nombre: '',
        marca: '',
        modelo: '',
        anio: new Date().getFullYear(),
        patente: '',
        tipoEquipo: 0,
        estadoEquipo: 0,
        faena: 0,
        activo: true
      });

      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error creating equipment:', err);
      setError('Error al crear el equipo');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div>
            <CardTitle>{isEditMode ? 'Editar Equipo' : 'Nuevo Equipo'}</CardTitle>
            <CardDescription>
              {isEditMode ? 'Modifica los datos del equipo' : 'Registrar un nuevo equipo en el sistema'}
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
            {/* Información Básica */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Información Básica</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="codigo">Código Interno *</Label>
                  <Input
                    id="codigo"
                    placeholder="Ej: CM-001"
                    value={formData.codigo}
                    onChange={(e) => handleInputChange('codigo', e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="nombre">Nombre del Equipo *</Label>
                  <Input
                    id="nombre"
                    placeholder="Ej: Camioneta Toyota Hilux"
                    value={formData.nombre}
                    onChange={(e) => handleInputChange('nombre', e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="marca">Marca</Label>
                  <Input
                    id="marca"
                    placeholder="Ej: Toyota"
                    value={formData.marca}
                    onChange={(e) => handleInputChange('marca', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="modelo">Modelo</Label>
                  <Input
                    id="modelo"
                    placeholder="Ej: Hilux"
                    value={formData.modelo}
                    onChange={(e) => handleInputChange('modelo', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="anio">Año</Label>
                  <Input
                    id="anio"
                    type="number"
                    min="1900"
                    max={new Date().getFullYear() + 1}
                    value={formData.anio}
                    onChange={(e) => handleInputChange('anio', parseInt(e.target.value))}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="patente">Patente</Label>
                <Input
                  id="patente"
                  placeholder="Ej: ABC-123"
                  value={formData.patente}
                  onChange={(e) => handleInputChange('patente', e.target.value)}
                />
              </div>
            </div>

            {/* Clasificación */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Clasificación</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="tipoEquipo">Tipo de Equipo *</Label>
                  <Select 
                    value={formData.tipoEquipo.toString()} 
                    onValueChange={(value) => handleInputChange('tipoEquipo', parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Seleccionar tipo" />
                    </SelectTrigger>
                    <SelectContent>
                      {tiposEquipo.map((tipo) => (
                        <SelectItem key={tipo.id} value={tipo.id.toString()}>
                          <div className="flex items-center gap-2">
                            <Tag className="h-4 w-4" />
                            {tipo.nombre}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="estadoEquipo">Estado Actual *</Label>
                  <Select 
                    value={formData.estadoEquipo.toString()} 
                    onValueChange={(value) => handleInputChange('estadoEquipo', parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Seleccionar estado" />
                    </SelectTrigger>
                    <SelectContent>
                      {estadosEquipo.map((estado) => (
                        <SelectItem key={estado.id} value={estado.id.toString()}>
                          <div className="flex items-center gap-2">
                            <Wrench className="h-4 w-4" />
                            {estado.nombre}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="faena">Ubicación (Faena)</Label>
                <Select 
                  value={formData.faena.toString()} 
                  onValueChange={(value) => handleInputChange('faena', parseInt(value))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar faena" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">Sin asignar</SelectItem>
                    {faenas.filter(f => f.activa).map((faena) => (
                      <SelectItem key={faena.id} value={faena.id.toString()}>
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4" />
                          {faena.nombre}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Estado */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Estado del Equipo</h3>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="activo"
                  checked={formData.activo}
                  onChange={(e) => handleInputChange('activo', e.target.checked)}
                  className="rounded border-gray-300"
                />
                <Label htmlFor="activo">Equipo activo en el sistema</Label>
              </div>
            </div>

            {/* Resumen */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium mb-2">Resumen del Equipo</h4>
              <div className="space-y-1 text-sm text-gray-600">
                <p><strong>Código:</strong> {formData.codigo || 'No especificado'}</p>
                <p><strong>Nombre:</strong> {formData.nombre || 'No especificado'}</p>
                <p><strong>Tipo:</strong> {tiposEquipo.find(t => t.id === formData.tipoEquipo)?.nombre || 'No seleccionado'}</p>
                <p><strong>Estado:</strong> {estadosEquipo.find(e => e.id === formData.estadoEquipo)?.nombre || 'No seleccionado'}</p>
                <p><strong>Ubicación:</strong> {faenas.find(f => f.id === formData.faena)?.nombre || 'Sin asignar'}</p>
                <p><strong>Activo:</strong> 
                  <Badge variant={formData.activo ? 'default' : 'secondary'} className="ml-2">
                    {formData.activo ? 'Sí' : 'No'}
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
                    Crear Equipo
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
