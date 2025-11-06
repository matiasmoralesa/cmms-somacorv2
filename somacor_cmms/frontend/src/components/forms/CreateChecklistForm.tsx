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
import { Loader2, ClipboardCheck, Wrench, User, Plus, X } from 'lucide-react';

interface CreateChecklistFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  checklistData?: any; // Para edición
}

interface ChecklistFormData {
  nombre: string;
  descripcion: string;
  idequipo: number;
  idtecnico: number;
  fecha_programada: string;
  items: ChecklistItem[];
  observaciones: string;
  activo: boolean;
}

interface ChecklistItem {
  id?: number;
  nombre: string;
  descripcion: string;
  tipo: 'verificacion' | 'medicion' | 'observacion';
  obligatorio: boolean;
  orden: number;
}

const CreateChecklistForm: React.FC<CreateChecklistFormProps> = ({
  isOpen,
  onClose,
  onSuccess,
  checklistData
}) => {
  const [formData, setFormData] = useState<ChecklistFormData>({
    nombre: '',
    descripcion: '',
    idequipo: 0,
    idtecnico: 0,
    fecha_programada: '',
    items: [],
    observaciones: '',
    activo: true
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [equipos, setEquipos] = useState<any[]>([]);
  const [tecnicos, setTecnicos] = useState<any[]>([]);

  const isEditMode = Boolean(checklistData);

  const tiposItem = [
    { value: 'verificacion', label: 'Verificación' },
    { value: 'medicion', label: 'Medición' },
    { value: 'observacion', label: 'Observación' }
  ];

  useEffect(() => {
    // Cargar equipos y técnicos
    const loadData = async () => {
      try {
        const [equiposResponse, tecnicosResponse] = await Promise.all([
          fetch('/api/v2/equipos/'),
          fetch('/api/v2/usuarios/')
        ]);

        if (equiposResponse.ok) {
          const equiposData = await equiposResponse.json();
          setEquipos(equiposData.results || equiposData);
        }

        if (tecnicosResponse.ok) {
          const tecnicosData = await tecnicosResponse.json();
          setTecnicos(tecnicosData.results || tecnicosData);
        }
      } catch (err) {
        console.error('Error cargando datos:', err);
      }
    };

    loadData();

    if (checklistData) {
      setFormData({
        nombre: checklistData.nombre || '',
        descripcion: checklistData.descripcion || '',
        idequipo: checklistData.idequipo || 0,
        idtecnico: checklistData.idtecnico || 0,
        fecha_programada: checklistData.fecha_programada || '',
        items: checklistData.items || [],
        observaciones: checklistData.observaciones || '',
        activo: checklistData.activo !== undefined ? checklistData.activo : true
      });
    } else {
      // Reset form for new checklist
      setFormData({
        nombre: '',
        descripcion: '',
        idequipo: 0,
        idtecnico: 0,
        fecha_programada: '',
        items: [],
        observaciones: '',
        activo: true
      });
    }
    setError(null);
  }, [checklistData, isOpen]);

  const handleInputChange = (field: keyof ChecklistFormData, value: string | boolean | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAddItem = () => {
    const newItem: ChecklistItem = {
      nombre: '',
      descripcion: '',
      tipo: 'verificacion',
      obligatorio: true,
      orden: formData.items.length + 1
    };

    setFormData(prev => ({
      ...prev,
      items: [...prev.items, newItem]
    }));
  };

  const handleUpdateItem = (index: number, field: keyof ChecklistItem, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const handleRemoveItem = (index: number) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  const validateForm = (): boolean => {
    if (!formData.nombre.trim()) {
      setError('El nombre del checklist es requerido');
      return false;
    }
    if (!formData.descripcion.trim()) {
      setError('La descripción es requerida');
      return false;
    }
    if (!formData.idequipo) {
      setError('Debe seleccionar un equipo');
      return false;
    }
    if (!formData.idtecnico) {
      setError('Debe seleccionar un técnico');
      return false;
    }
    if (!formData.fecha_programada) {
      setError('La fecha programada es requerida');
      return false;
    }
    if (formData.items.length === 0) {
      setError('Debe agregar al menos un item al checklist');
      return false;
    }

    // Validar items
    for (let i = 0; i < formData.items.length; i++) {
      const item = formData.items[i];
      if (!item.nombre.trim()) {
        setError(`El item ${i + 1} debe tener un nombre`);
        return false;
      }
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
        ? `/api/v2/checklist-instance/${checklistData.idchecklistinstance}/` 
        : '/api/v2/checklist-instance/';
      
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
        throw new Error(errorData.detail || errorData.message || 'Error al guardar el checklist');
      }

      const result = await response.json();
      console.log(`${isEditMode ? 'Checklist actualizado' : 'Checklist creado'} exitosamente:`, result);
      
      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error al guardar el checklist:', err);
      setError(err instanceof Error ? err.message : 'Error al guardar el checklist');
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
      title={`${isEditMode ? 'Editar Checklist' : 'Nuevo Checklist'}`}
      size="xlarge"
    >
      <div className="max-h-[70vh] overflow-y-auto">

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Nombre del Checklist */}
            <div className="md:col-span-2">
              <Label htmlFor="nombre" className="text-sm font-medium">
                Nombre del Checklist *
              </Label>
              <Input
                id="nombre"
                type="text"
                placeholder="Ej: Checklist Diario Compresor A-101"
                value={formData.nombre}
                onChange={(e) => handleInputChange('nombre', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Descripción */}
            <div className="md:col-span-2">
              <Label htmlFor="descripcion" className="text-sm font-medium">
                Descripción *
              </Label>
              <Textarea
                id="descripcion"
                placeholder="Descripción del checklist..."
                value={formData.descripcion}
                onChange={(e) => handleInputChange('descripcion', e.target.value)}
                disabled={loading}
                rows={2}
                className="mt-1"
              />
            </div>

            {/* Equipo */}
            <div>
              <Label htmlFor="idequipo" className="text-sm font-medium flex items-center gap-1">
                <Wrench className="h-4 w-4" />
                Equipo *
              </Label>
              <Select
                value={formData.idequipo.toString()}
                onValueChange={(value) => handleInputChange('idequipo', parseInt(value))}
                disabled={loading}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Seleccionar equipo" />
                </SelectTrigger>
                <SelectContent>
                  {equipos.map((equipo) => (
                    <SelectItem key={equipo.idequipo} value={equipo.idequipo.toString()}>
                      {equipo.nombreequipo} ({equipo.codigointerno})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Técnico */}
            <div>
              <Label htmlFor="idtecnico" className="text-sm font-medium flex items-center gap-1">
                <User className="h-4 w-4" />
                Técnico Asignado *
              </Label>
              <Select
                value={formData.idtecnico.toString()}
                onValueChange={(value) => handleInputChange('idtecnico', parseInt(value))}
                disabled={loading}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Seleccionar técnico" />
                </SelectTrigger>
                <SelectContent>
                  {tecnicos.map((tecnico) => (
                    <SelectItem key={tecnico.idusuario} value={tecnico.idusuario.toString()}>
                      {tecnico.nombres} {tecnico.apellidos}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Fecha Programada */}
            <div className="md:col-span-2">
              <Label htmlFor="fecha_programada" className="text-sm font-medium">
                Fecha Programada *
              </Label>
              <Input
                id="fecha_programada"
                type="datetime-local"
                value={formData.fecha_programada}
                onChange={(e) => handleInputChange('fecha_programada', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>
          </div>

          {/* Items del Checklist */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <Label className="text-sm font-medium">
                Items del Checklist ({formData.items.length})
              </Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddItem}
                disabled={loading}
              >
                <Plus className="h-4 w-4 mr-2" />
                Agregar Item
              </Button>
            </div>

            <div className="space-y-3 max-h-60 overflow-y-auto">
              {formData.items.map((item, index) => (
                <div key={index} className="p-4 border rounded-lg bg-muted/30">
                  <div className="flex items-center justify-between mb-3">
                    <Badge variant="secondary">Item {index + 1}</Badge>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveItem(index)}
                      disabled={loading}
                      className="text-red-600 hover:text-red-700"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <Label className="text-xs text-muted-foreground">Nombre *</Label>
                      <Input
                        placeholder="Nombre del item"
                        value={item.nombre}
                        onChange={(e) => handleUpdateItem(index, 'nombre', e.target.value)}
                        disabled={loading}
                        className="h-8"
                      />
                    </div>

                    <div>
                      <Label className="text-xs text-muted-foreground">Tipo</Label>
                      <Select
                        value={item.tipo}
                        onValueChange={(value: any) => handleUpdateItem(index, 'tipo', value)}
                        disabled={loading}
                      >
                        <SelectTrigger className="h-8">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {tiposItem.map((tipo) => (
                            <SelectItem key={tipo.value} value={tipo.value}>
                              {tipo.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="md:col-span-2">
                      <Label className="text-xs text-muted-foreground">Descripción</Label>
                      <Input
                        placeholder="Descripción del item"
                        value={item.descripcion}
                        onChange={(e) => handleUpdateItem(index, 'descripcion', e.target.value)}
                        disabled={loading}
                        className="h-8"
                      />
                    </div>

                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id={`obligatorio-${index}`}
                        checked={item.obligatorio}
                        onCheckedChange={(checked) => handleUpdateItem(index, 'obligatorio', checked as boolean)}
                        disabled={loading}
                      />
                      <Label htmlFor={`obligatorio-${index}`} className="text-xs">
                        Item obligatorio
                      </Label>
                    </div>
                  </div>
                </div>
              ))}

              {formData.items.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <ClipboardCheck className="mx-auto h-12 w-12 mb-4 opacity-50" />
                  <p>No hay items en el checklist</p>
                  <p className="text-sm">Agrega items para crear un checklist completo</p>
                </div>
              )}
            </div>
          </div>

          {/* Observaciones */}
          <div>
            <Label htmlFor="observaciones" className="text-sm font-medium">
              Observaciones
            </Label>
            <Textarea
              id="observaciones"
              placeholder="Observaciones adicionales sobre el checklist..."
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
              Checklist activo
            </Label>
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
                  <ClipboardCheck className="mr-2 h-4 w-4" />
                  {isEditMode ? 'Actualizar' : 'Crear'} Checklist
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
};

export default CreateChecklistForm;
