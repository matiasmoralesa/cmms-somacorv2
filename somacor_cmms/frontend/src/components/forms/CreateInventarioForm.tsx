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
import { Loader2, Package, MapPin, DollarSign } from 'lucide-react';
import { inventarioService } from '@/services/inventarioService';
import apiClient from '@/api/apiClient';

interface CreateInventarioFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  inventarioData?: any; // Para edición
}

interface InventarioFormData {
  codigo: string;
  nombre: string;
  descripcion: string;
  categoria: string;
  cantidad: number;
  cantidad_minima: number;
  ubicacion: string;
  costo_unitario: number;
  proveedor: string;
  observaciones: string;
  activo: boolean;
}

const CreateInventarioForm: React.FC<CreateInventarioFormProps> = ({
  isOpen,
  onClose,
  onSuccess,
  inventarioData
}) => {
  const [formData, setFormData] = useState<InventarioFormData>({
    codigo: '',
    nombre: '',
    descripcion: '',
    categoria: '',
    cantidad: 0,
    cantidad_minima: 0,
    ubicacion: '',
    costo_unitario: 0,
    proveedor: '',
    observaciones: '',
    activo: true
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [faenas, setFaenas] = useState<any[]>([]);
  const [loadingFaenas, setLoadingFaenas] = useState(false);

  const isEditMode = Boolean(inventarioData);

  const categorias = [
    'Filtros',
    'Rodamientos',
    'Lubricantes',
    'Herramientas',
    'Repuestos Eléctricos',
    'Repuestos Mecánicos',
    'Repuestos Hidráulicos',
    'Repuestos Neumáticos',
    'Materiales de Consumo',
    'Equipos de Seguridad',
    'Instrumentación',
    'Otros'
  ];

  // Cargar faenas al montar el componente
  useEffect(() => {
    const fetchFaenas = async () => {
      try {
        setLoadingFaenas(true);
        const response = await apiClient.get('/v2/faenas/');
        const faenasData = response.data.results || response.data || [];
        setFaenas(faenasData);
      } catch (err) {
        console.error('Error al cargar faenas:', err);
        setFaenas([]);
      } finally {
        setLoadingFaenas(false);
      }
    };

    if (isOpen) {
      fetchFaenas();
    }
  }, [isOpen]);

  useEffect(() => {
    if (inventarioData) {
      setFormData({
        codigo: inventarioData.codigo || '',
        nombre: inventarioData.nombre || '',
        descripcion: inventarioData.descripcion || '',
        categoria: inventarioData.categoria || '',
        cantidad: inventarioData.cantidad || 0,
        cantidad_minima: inventarioData.cantidad_minima || 0,
        ubicacion: inventarioData.ubicacion || '',
        costo_unitario: inventarioData.costo_unitario || 0,
        proveedor: inventarioData.proveedor || '',
        observaciones: inventarioData.observaciones || '',
        activo: inventarioData.activo !== undefined ? inventarioData.activo : true
      });
    } else {
      // Reset form for new inventario
      setFormData({
        codigo: '',
        nombre: '',
        descripcion: '',
        categoria: '',
        cantidad: 0,
        cantidad_minima: 0,
        ubicacion: '',
        costo_unitario: 0,
        proveedor: '',
        observaciones: '',
        activo: true
      });
    }
    setError(null);
  }, [inventarioData, isOpen]);

  const handleInputChange = (field: keyof InventarioFormData, value: string | boolean | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = (): boolean => {
    if (!formData.codigo.trim()) {
      setError('El código es requerido');
      return false;
    }
    if (!formData.nombre.trim()) {
      setError('El nombre es requerido');
      return false;
    }
    if (!formData.categoria) {
      setError('La categoría es requerida');
      return false;
    }
    if (formData.cantidad < 0) {
      setError('La cantidad no puede ser negativa');
      return false;
    }
    if (formData.cantidad_minima < 0) {
      setError('La cantidad mínima no puede ser negativa');
      return false;
    }
    if (formData.costo_unitario < 0) {
      setError('El costo unitario no puede ser negativo');
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
      const itemData = {
        codigo: formData.codigo,
        nombre: formData.nombre,
        categoria: formData.categoria,
        stock_actual: formData.cantidad,
        stock_minimo: formData.cantidad_minima,
        unidad: 'unidad',
        ubicacion: formData.ubicacion,
        proveedor: formData.proveedor,
        precio_unitario: formData.costo_unitario,
        estado: (formData.cantidad <= formData.cantidad_minima ? 'bajo_stock' : 'disponible') as 'disponible' | 'bajo_stock' | 'agotado'
      };

      if (isEditMode && inventarioData?.id) {
        // Actualizar item existente
        await inventarioService.update(parseInt(inventarioData.id), itemData);
      } else {
        // Crear nuevo item
        await inventarioService.create(itemData);
      }

      alert(isEditMode ? 'Item de inventario actualizado exitosamente' : 'Item de inventario creado exitosamente');
      
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error al guardar el item de inventario:', err);
      
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
        setError('Error al guardar el item de inventario. Por favor intenta nuevamente.');
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
      title={`${isEditMode ? 'Editar Item de Inventario' : 'Nuevo Item de Inventario'}`}
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
            {/* Código */}
            <div>
              <Label htmlFor="codigo" className="text-sm font-medium">
                Código *
              </Label>
              <Input
                id="codigo"
                type="text"
                placeholder="Ej: FILT-001, ROD-6308"
                value={formData.codigo}
                onChange={(e) => handleInputChange('codigo', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Nombre */}
            <div>
              <Label htmlFor="nombre" className="text-sm font-medium">
                Nombre *
              </Label>
              <Input
                id="nombre"
                type="text"
                placeholder="Ej: Filtro de Aire Industrial"
                value={formData.nombre}
                onChange={(e) => handleInputChange('nombre', e.target.value)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Categoría */}
            <div>
              <Label htmlFor="categoria" className="text-sm font-medium">
                Categoría *
              </Label>
              <Select
                value={formData.categoria}
                onValueChange={(value) => handleInputChange('categoria', value)}
                disabled={loading}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Seleccionar categoría" />
                </SelectTrigger>
                <SelectContent>
                  {categorias.map((categoria) => (
                    <SelectItem key={categoria} value={categoria}>
                      {categoria}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Ubicación (Faena) */}
            <div>
              <Label htmlFor="ubicacion" className="text-sm font-medium flex items-center gap-1">
                <MapPin className="h-4 w-4" />
                Ubicación (Faena)
              </Label>
              <Select
                value={formData.ubicacion}
                onValueChange={(value) => handleInputChange('ubicacion', value)}
                disabled={loading || loadingFaenas}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder={loadingFaenas ? "Cargando faenas..." : "Seleccionar faena"} />
                </SelectTrigger>
                <SelectContent>
                  {faenas.length === 0 && !loadingFaenas && (
                    <SelectItem value="sin-faenas" disabled>
                      No hay faenas disponibles
                    </SelectItem>
                  )}
                  {faenas.map((faena) => (
                    <SelectItem key={faena.idfaena} value={faena.nombrefaena}>
                      {faena.nombrefaena}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Cantidad */}
            <div>
              <Label htmlFor="cantidad" className="text-sm font-medium">
                Cantidad Actual
              </Label>
              <Input
                id="cantidad"
                type="number"
                min="0"
                step="1"
                value={formData.cantidad}
                onChange={(e) => handleInputChange('cantidad', parseInt(e.target.value) || 0)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Cantidad Mínima */}
            <div>
              <Label htmlFor="cantidad_minima" className="text-sm font-medium">
                Stock Mínimo
              </Label>
              <Input
                id="cantidad_minima"
                type="number"
                min="0"
                step="1"
                value={formData.cantidad_minima}
                onChange={(e) => handleInputChange('cantidad_minima', parseInt(e.target.value) || 0)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Costo Unitario */}
            <div>
              <Label htmlFor="costo_unitario" className="text-sm font-medium flex items-center gap-1">
                <DollarSign className="h-4 w-4" />
                Costo Unitario
              </Label>
              <Input
                id="costo_unitario"
                type="number"
                min="0"
                step="0.01"
                value={formData.costo_unitario}
                onChange={(e) => handleInputChange('costo_unitario', parseFloat(e.target.value) || 0)}
                disabled={loading}
                className="mt-1"
              />
            </div>

            {/* Proveedor */}
            <div>
              <Label htmlFor="proveedor" className="text-sm font-medium">
                Proveedor
              </Label>
              <Input
                id="proveedor"
                type="text"
                placeholder="Nombre del proveedor"
                value={formData.proveedor}
                onChange={(e) => handleInputChange('proveedor', e.target.value)}
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
                placeholder="Descripción detallada del item..."
                value={formData.descripcion}
                onChange={(e) => handleInputChange('descripcion', e.target.value)}
                disabled={loading}
                rows={3}
                className="mt-1"
              />
            </div>

            {/* Observaciones */}
            <div className="md:col-span-2">
              <Label htmlFor="observaciones" className="text-sm font-medium">
                Observaciones
              </Label>
              <Textarea
                id="observaciones"
                placeholder="Observaciones adicionales sobre el item..."
                value={formData.observaciones}
                onChange={(e) => handleInputChange('observaciones', e.target.value)}
                disabled={loading}
                rows={2}
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
                Item activo en inventario
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
                  <Package className="mr-2 h-4 w-4" />
                  {isEditMode ? 'Actualizar' : 'Crear'} Item
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
};

export default CreateInventarioForm;
