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
import { Badge } from '@/components/ui/badge';
import { Loader2, User, Phone, Mail, Wrench, X, Plus } from 'lucide-react';
import { tecnicosService } from '@/services/tecnicosService';

interface CreateTecnicoFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  tecnicoData?: any; // Para edición
}

interface TecnicoFormData {
  nombres: string;
  apellidos: string;
  email: string;
  telefono: string;
  especialidades: string[];
  activo: boolean;
  observaciones: string;
  idrol: number;
}

const CreateTecnicoForm: React.FC<CreateTecnicoFormProps> = ({
  isOpen,
  onClose,
  onSuccess,
  tecnicoData
}) => {
  const [formData, setFormData] = useState<TecnicoFormData>({
    nombres: '',
    apellidos: '',
    email: '',
    telefono: '',
    especialidades: [],
    activo: true,
    observaciones: '',
    idrol: 3 // Rol de técnico por defecto
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newEspecialidad, setNewEspecialidad] = useState('');
  const [roles, setRoles] = useState<any[]>([]);

  const isEditMode = Boolean(tecnicoData);

  // Especialidades predefinidas
  const especialidadesDisponibles = [
    'Compresores',
    'Sistemas Neumáticos',
    'Mantenimiento Preventivo',
    'Bombas Centrífugas',
    'Sistemas Hidráulicos',
    'Motores Eléctricos',
    'Sistemas Eléctricos',
    'Automatización',
    'Mecánica Industrial',
    'Soldadura',
    'Instrumentación',
    'Refrigeración Industrial'
  ];

  useEffect(() => {
    // Cargar roles disponibles
    const loadRoles = async () => {
      try {
        const response = await fetch('/api/v2/roles/');
        if (response.ok) {
          const data = await response.json();
          setRoles(data.results || data);
        }
      } catch (err) {
        console.error('Error cargando roles:', err);
      }
    };
    
    loadRoles();

    if (tecnicoData) {
      setFormData({
        nombres: tecnicoData.nombres || '',
        apellidos: tecnicoData.apellidos || '',
        email: tecnicoData.email || '',
        telefono: tecnicoData.telefono || '',
        especialidades: tecnicoData.especialidades || [],
        activo: tecnicoData.activo !== undefined ? tecnicoData.activo : true,
        observaciones: tecnicoData.observaciones || '',
        idrol: tecnicoData.idrol || 3
      });
    } else {
      // Reset form for new tecnico
      setFormData({
        nombres: '',
        apellidos: '',
        email: '',
        telefono: '',
        especialidades: [],
        activo: true,
        observaciones: '',
        idrol: 3
      });
    }
    setError(null);
  }, [tecnicoData, isOpen]);

  const handleInputChange = (field: keyof TecnicoFormData, value: string | boolean | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAddEspecialidad = () => {
    if (newEspecialidad.trim() && !formData.especialidades.includes(newEspecialidad.trim())) {
      setFormData(prev => ({
        ...prev,
        especialidades: [...prev.especialidades, newEspecialidad.trim()]
      }));
      setNewEspecialidad('');
    }
  };

  const handleRemoveEspecialidad = (especialidad: string) => {
    setFormData(prev => ({
      ...prev,
      especialidades: prev.especialidades.filter(esp => esp !== especialidad)
    }));
  };

  const handleSelectEspecialidad = (especialidad: string) => {
    if (!formData.especialidades.includes(especialidad)) {
      setFormData(prev => ({
        ...prev,
        especialidades: [...prev.especialidades, especialidad]
      }));
    }
  };

  const validateForm = (): boolean => {
    if (!formData.nombres.trim()) {
      setError('Los nombres son requeridos');
      return false;
    }
    if (!formData.apellidos.trim()) {
      setError('Los apellidos son requeridos');
      return false;
    }
    if (!formData.email.trim()) {
      setError('El email es requerido');
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError('El email no tiene un formato válido');
      return false;
    }
    if (!formData.idrol) {
      setError('Debe seleccionar un rol');
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
      // TODO: Implementar creación/actualización de técnico
      // Por ahora, solo simular
      console.log('Guardando técnico:', formData);
      
      // Simular delay de API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      alert(isEditMode ? 'Técnico actualizado exitosamente' : 'Técnico creado exitosamente');
      
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error al guardar el técnico:', err);
      
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
        setError('Error al guardar el técnico. Por favor intenta nuevamente.');
      }
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
      title={`${isEditMode ? 'Editar Técnico' : 'Nuevo Técnico'}`}
      size="large"
    >
      <div className="max-h-[70vh] overflow-y-auto">

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Nombres */}
            <div>
              <Label htmlFor="nombres" className="text-sm font-medium">
                Nombres *
              </Label>
              <Input
                id="nombres"
                type="text"
                placeholder="Juan Carlos"
                value={formData.nombres}
                onChange={(e) => handleInputChange('nombres', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Apellidos */}
            <div>
              <Label htmlFor="apellidos" className="text-sm font-medium">
                Apellidos *
              </Label>
              <Input
                id="apellidos"
                type="text"
                placeholder="Pérez González"
                value={formData.apellidos}
                onChange={(e) => handleInputChange('apellidos', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Email */}
            <div>
              <Label htmlFor="email" className="text-sm font-medium flex items-center gap-1">
                <Mail className="h-4 w-4" />
                Email *
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="juan.perez@somacor.com"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Teléfono */}
            <div>
              <Label htmlFor="telefono" className="text-sm font-medium flex items-center gap-1">
                <Phone className="h-4 w-4" />
                Teléfono
              </Label>
              <Input
                id="telefono"
                type="tel"
                placeholder="+56 9 1234 5678"
                value={formData.telefono}
                onChange={(e) => handleInputChange('telefono', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Rol */}
            <div className="md:col-span-2">
              <Label htmlFor="idrol" className="text-sm font-medium">
                Rol *
              </Label>
              <Select
                value={formData.idrol.toString()}
                onValueChange={(value) => handleInputChange('idrol', parseInt(value))}
                disabled={loading}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Seleccionar rol" />
                </SelectTrigger>
                <SelectContent>
                  {roles.map((rol) => (
                    <SelectItem key={rol.idrol} value={rol.idrol.toString()}>
                      {rol.nombrerol}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Especialidades */}
            <div className="md:col-span-2">
              <Label className="text-sm font-medium flex items-center gap-1">
                <Wrench className="h-4 w-4" />
                Especialidades
              </Label>
              
              {/* Especialidades actuales */}
              {formData.especialidades.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2 mb-3">
                  {formData.especialidades.map((especialidad) => (
                    <Badge key={especialidad} variant="secondary" className="flex items-center gap-1">
                      {especialidad}
                      <X 
                        className="h-3 w-3 cursor-pointer hover:text-red-600" 
                        onClick={() => handleRemoveEspecialidad(especialidad)}
                      />
                    </Badge>
                  ))}
                </div>
              )}

              {/* Agregar nueva especialidad */}
              <div className="flex gap-2 mb-3">
                <Input
                  placeholder="Nueva especialidad..."
                  value={newEspecialidad}
                  onChange={(e) => setNewEspecialidad(e.target.value)}
                  disabled={loading}
                  className="flex-1"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddEspecialidad();
                    }
                  }}
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAddEspecialidad}
                  disabled={loading || !newEspecialidad.trim()}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>

              {/* Especialidades predefinidas */}
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">Especialidades disponibles:</Label>
                <div className="flex flex-wrap gap-1">
                  {especialidadesDisponibles.map((especialidad) => (
                    <Button
                      key={especialidad}
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => handleSelectEspecialidad(especialidad)}
                      disabled={loading || formData.especialidades.includes(especialidad)}
                      className="text-xs"
                    >
                      {especialidad}
                    </Button>
                  ))}
                </div>
              </div>
            </div>

            {/* Observaciones */}
            <div className="md:col-span-2">
              <Label htmlFor="observaciones" className="text-sm font-medium">
                Observaciones
              </Label>
              <Textarea
                id="observaciones"
                placeholder="Observaciones adicionales sobre el técnico..."
                value={formData.observaciones}
                onChange={(e) => handleInputChange('observaciones', e.target.value)}
                disabled={loading}
                rows={3}
                className="mt-1"
              />
            </div>

            {/* Estado Activo */}
            <div className="md:col-span-2 flex items-center space-x-2">
              <Checkbox
                id="activo"
                checked={formData.activo}
                onCheckedChange={(checked) => handleInputChange('activo', checked as boolean)}
                disabled={loading}
              />
              <Label htmlFor="activo" className="text-sm font-medium">
                Técnico activo
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
                  <User className="mr-2 h-4 w-4" />
                  {isEditMode ? 'Actualizar' : 'Crear'} Técnico
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
};

export default CreateTecnicoForm;
