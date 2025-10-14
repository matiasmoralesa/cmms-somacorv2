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
import { Loader2, MapPin, Phone, Mail, Building2 } from 'lucide-react';

interface CreateFaenaFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  faenaData?: any; // Para edición
}

interface FaenaFormData {
  nombrefaena: string;
  ubicacion: string;
  descripcion: string;
  contacto: string;
  telefono: string;
  email: string;
  activa: boolean;
  direccion: string;
  ciudad: string;
  region: string;
}

const CreateFaenaForm: React.FC<CreateFaenaFormProps> = ({
  isOpen,
  onClose,
  onSuccess,
  faenaData
}) => {
  const [formData, setFormData] = useState<FaenaFormData>({
    nombrefaena: '',
    ubicacion: '',
    descripcion: '',
    contacto: '',
    telefono: '',
    email: '',
    activa: true,
    direccion: '',
    ciudad: '',
    region: ''
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [regions] = useState([
    'Región Metropolitana',
    'Región de Valparaíso',
    'Región del Biobío',
    'Región de Antofagasta',
    'Región de Atacama',
    'Región de Coquimbo',
    'Región del Maule',
    'Región de Ñuble',
    'Región de La Araucanía',
    'Región de Los Ríos',
    'Región de Los Lagos',
    'Región de Aysén',
    'Región de Magallanes'
  ]);

  const isEditMode = Boolean(faenaData);

  useEffect(() => {
    if (faenaData) {
      setFormData({
        nombrefaena: faenaData.nombrefaena || '',
        ubicacion: faenaData.ubicacion || '',
        descripcion: faenaData.descripcion || '',
        contacto: faenaData.contacto || '',
        telefono: faenaData.telefono || '',
        email: faenaData.email || '',
        activa: faenaData.activa !== undefined ? faenaData.activa : true,
        direccion: faenaData.direccion || '',
        ciudad: faenaData.ciudad || '',
        region: faenaData.region || ''
      });
    } else {
      // Reset form for new faena
      setFormData({
        nombrefaena: '',
        ubicacion: '',
        descripcion: '',
        contacto: '',
        telefono: '',
        email: '',
        activa: true,
        direccion: '',
        ciudad: '',
        region: ''
      });
    }
    setError(null);
  }, [faenaData, isOpen]);

  const handleInputChange = (field: keyof FaenaFormData, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = (): boolean => {
    if (!formData.nombrefaena.trim()) {
      setError('El nombre de la faena es requerido');
      return false;
    }
    if (!formData.ubicacion.trim()) {
      setError('La ubicación es requerida');
      return false;
    }
    if (!formData.contacto.trim()) {
      setError('El contacto es requerido');
      return false;
    }
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError('El email no tiene un formato válido');
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
        ? `/api/v2/faenas/${faenaData.idfaena}/` 
        : '/api/v2/faenas/';
      
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
        throw new Error(errorData.detail || errorData.message || 'Error al guardar la faena');
      }

      const result = await response.json();
      console.log(`${isEditMode ? 'Faena actualizada' : 'Faena creada'} exitosamente:`, result);
      
      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error al guardar la faena:', err);
      setError(err instanceof Error ? err.message : 'Error al guardar la faena');
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
      title={`${isEditMode ? 'Editar Faena' : 'Nueva Faena'}`}
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
            {/* Nombre de la Faena */}
            <div className="md:col-span-2">
              <Label htmlFor="nombrefaena" className="text-sm font-medium">
                Nombre de la Faena *
              </Label>
              <Input
                id="nombrefaena"
                type="text"
                placeholder="Ej: Planta Norte, Mina Central"
                value={formData.nombrefaena}
                onChange={(e) => handleInputChange('nombrefaena', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Ubicación */}
            <div className="md:col-span-2">
              <Label htmlFor="ubicacion" className="text-sm font-medium">
                Ubicación *
              </Label>
              <Input
                id="ubicacion"
                type="text"
                placeholder="Ej: Región Metropolitana, Santiago"
                value={formData.ubicacion}
                onChange={(e) => handleInputChange('ubicacion', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Dirección */}
            <div>
              <Label htmlFor="direccion" className="text-sm font-medium">
                Dirección
              </Label>
              <Input
                id="direccion"
                type="text"
                placeholder="Dirección específica"
                value={formData.direccion}
                onChange={(e) => handleInputChange('direccion', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Ciudad */}
            <div>
              <Label htmlFor="ciudad" className="text-sm font-medium">
                Ciudad
              </Label>
              <Input
                id="ciudad"
                type="text"
                placeholder="Ciudad"
                value={formData.ciudad}
                onChange={(e) => handleInputChange('ciudad', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Región */}
            <div>
              <Label htmlFor="region" className="text-sm font-medium">
                Región
              </Label>
              <Select
                value={formData.region}
                onValueChange={(value) => handleInputChange('region', value)}
                disabled={loading}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Seleccionar región" />
                </SelectTrigger>
                <SelectContent>
                  {regions.map((region) => (
                    <SelectItem key={region} value={region}>
                      {region}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Contacto */}
            <div>
              <Label htmlFor="contacto" className="text-sm font-medium">
                Contacto *
              </Label>
              <Input
                id="contacto"
                type="text"
                placeholder="Nombre del responsable"
                value={formData.contacto}
                onChange={(e) => handleInputChange('contacto', e.target.value)}
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

            {/* Email */}
            <div>
              <Label htmlFor="email" className="text-sm font-medium flex items-center gap-1">
                <Mail className="h-4 w-4" />
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="contacto@faena.com"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Descripción */}
            <div className="md:col-span-2">
              <Label htmlFor="descripcion" className="text-sm font-medium">
                Descripción
              </Label>
              <Textarea
                id="descripcion"
                placeholder="Descripción adicional de la faena..."
                value={formData.descripcion}
                onChange={(e) => handleInputChange('descripcion', e.target.value)}
                disabled={loading}
                rows={3}
                className="mt-1"
              />
            </div>

            {/* Estado Activo */}
            <div className="md:col-span-2 flex items-center space-x-2">
              <Checkbox
                id="activa"
                checked={formData.activa}
                onCheckedChange={(checked) => handleInputChange('activa', checked as boolean)}
                disabled={loading}
              />
              <Label htmlFor="activa" className="text-sm font-medium">
                Faena activa
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
                  <MapPin className="mr-2 h-4 w-4" />
                  {isEditMode ? 'Actualizar' : 'Crear'} Faena
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
};

export default CreateFaenaForm;
