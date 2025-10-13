import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import Modal from '@/components/ui/Modal';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Loader2, Wrench, Settings } from 'lucide-react';

interface CreateTipoEquipoFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  tipoEquipoData?: any; // Para edición
}

interface TipoEquipoFormData {
  nombretipo: string;
  descripciontipo: string;
  activo: boolean;
  frecuencia_mantenimiento: string;
  observaciones: string;
}

const CreateTipoEquipoForm: React.FC<CreateTipoEquipoFormProps> = ({
  isOpen,
  onClose,
  onSuccess,
  tipoEquipoData
}) => {
  const [formData, setFormData] = useState<TipoEquipoFormData>({
    nombretipo: '',
    descripciontipo: '',
    activo: true,
    frecuencia_mantenimiento: 'Mensual',
    observaciones: ''
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditMode = Boolean(tipoEquipoData);

  const frecuenciasMantenimiento = [
    { value: 'Diario', label: 'Diario' },
    { value: 'Semanal', label: 'Semanal' },
    { value: 'Mensual', label: 'Mensual' },
    { value: 'Bimensual', label: 'Bimensual' },
    { value: 'Trimestral', label: 'Trimestral' },
    { value: 'Semestral', label: 'Semestral' },
    { value: 'Anual', label: 'Anual' }
  ];

  useEffect(() => {
    if (tipoEquipoData) {
      setFormData({
        nombretipo: tipoEquipoData.nombretipo || '',
        descripciontipo: tipoEquipoData.descripciontipo || '',
        activo: tipoEquipoData.activo !== undefined ? tipoEquipoData.activo : true,
        frecuencia_mantenimiento: tipoEquipoData.frecuencia_mantenimiento || 'Mensual',
        observaciones: tipoEquipoData.observaciones || ''
      });
    } else {
      // Reset form for new tipo equipo
      setFormData({
        nombretipo: '',
        descripciontipo: '',
        activo: true,
        frecuencia_mantenimiento: 'Mensual',
        observaciones: ''
      });
    }
    setError(null);
  }, [tipoEquipoData, isOpen]);

  const handleInputChange = (field: keyof TipoEquipoFormData, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = (): boolean => {
    if (!formData.nombretipo.trim()) {
      setError('El nombre del tipo de equipo es requerido');
      return false;
    }
    if (!formData.descripciontipo.trim()) {
      setError('La descripción es requerida');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const endpoint = isEditMode 
        ? `/api/v2/tipos-equipo/${tipoEquipoData.idtipoequipo}/` 
        : '/api/v2/tipos-equipo/';
      
      const method = isEditMode ? 'PUT' : 'POST';

      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || errorData.message || 'Error al guardar el tipo de equipo');
      }

      const result = await response.json();
      console.log(`${isEditMode ? 'Tipo de equipo actualizado' : 'Tipo de equipo creado'} exitosamente:`, result);
      
      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error al guardar el tipo de equipo:', err);
      setError(err instanceof Error ? err.message : 'Error al guardar el tipo de equipo');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setError(null);
      onClose();
    }
  };

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose}
      title={`${isEditMode ? 'Editar Tipo de Equipo' : 'Nuevo Tipo de Equipo'}`}
      size="medium"
    >
      <div className="max-h-[70vh] overflow-y-auto">

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            {/* Nombre del Tipo */}
            <div>
              <Label htmlFor="nombretipo" className="text-sm font-medium">
                Nombre del Tipo *
              </Label>
              <Input
                id="nombretipo"
                type="text"
                placeholder="Ej: Compresores, Bombas, Motores"
                value={formData.nombretipo}
                onChange={(e) => handleInputChange('nombretipo', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Descripción */}
            <div>
              <Label htmlFor="descripciontipo" className="text-sm font-medium">
                Descripción *
              </Label>
              <Textarea
                id="descripciontipo"
                placeholder="Descripción detallada del tipo de equipo..."
                value={formData.descripciontipo}
                onChange={(e) => handleInputChange('descripciontipo', e.target.value)}
                disabled={loading}
                rows={3}
                className="mt-1"
              />
            </div>

            {/* Frecuencia de Mantenimiento */}
            <div>
              <Label htmlFor="frecuencia_mantenimiento" className="text-sm font-medium flex items-center gap-1">
                <Settings className="h-4 w-4" />
                Frecuencia de Mantenimiento
              </Label>
              <Select
                value={formData.frecuencia_mantenimiento}
                onValueChange={(value) => handleInputChange('frecuencia_mantenimiento', value)}
                disabled={loading}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Seleccionar frecuencia" />
                </SelectTrigger>
                <SelectContent>
                  {frecuenciasMantenimiento.map((frecuencia) => (
                    <SelectItem key={frecuencia.value} value={frecuencia.value}>
                      {frecuencia.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Observaciones */}
            <div>
              <Label htmlFor="observaciones" className="text-sm font-medium">
                Observaciones
              </Label>
              <Textarea
                id="observaciones"
                placeholder="Observaciones adicionales sobre este tipo de equipo..."
                value={formData.observaciones}
                onChange={(e) => handleInputChange('observaciones', e.target.value)}
                disabled={loading}
                rows={2}
                className="mt-1"
              />
            </div>

            {/* Estado Activo */}
            <div className="flex items-center space-x-2">
              <Checkbox
                id="activo"
                checked={formData.activo}
                onCheckedChange={(checked) => handleInputChange('activo', checked as boolean)}
                disabled={loading}
              />
              <Label htmlFor="activo" className="text-sm font-medium">
                Tipo de equipo activo
              </Label>
            </div>
          </div>

          <div className="flex gap-2 justify-end pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={loading}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="min-w-[120px]"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Guardando...
                </>
              ) : (
                <>
                  <Wrench className="mr-2 h-4 w-4" />
                  {isEditMode ? 'Actualizar' : 'Crear'} Tipo
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
};

export default CreateTipoEquipoForm;
