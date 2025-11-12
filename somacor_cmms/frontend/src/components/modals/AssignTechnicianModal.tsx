import React, { useState, useEffect } from 'react';
import { User, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import Modal from '@/components/ui/Modal';
import apiClient from '@/api/apiClient';

interface Technician {
  idtecnico: number;
  nombre_completo: string;
  especialidades_list: string[];
  ordenes_activas: number;
  estado: string;
}

interface AssignTechnicianModalProps {
  isOpen: boolean;
  onClose: () => void;
  maintenanceId: string;
  maintenanceTitle: string;
  onSuccess: () => void;
}

const AssignTechnicianModal: React.FC<AssignTechnicianModalProps> = ({
  isOpen,
  onClose,
  maintenanceId,
  maintenanceTitle,
  onSuccess
}) => {
  const [technicians, setTechnicians] = useState<Technician[]>([]);
  const [selectedTechnician, setSelectedTechnician] = useState('');
  const [estimatedTime, setEstimatedTime] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingTechnicians, setLoadingTechnicians] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchTechnicians();
    }
  }, [isOpen]);

  const fetchTechnicians = async () => {
    try {
      setLoadingTechnicians(true);
      const response = await apiClient.get('/v2/tecnicos/');
      const techs = response.data.results || response.data || [];
      
      // Filtrar solo técnicos activos y disponibles
      const techsActivos = techs.filter((tech: any) => 
        tech.activo && tech.estado !== 'no_disponible'
      );
      
      setTechnicians(techsActivos);
    } catch (err) {
      console.error('Error al cargar técnicos:', err);
      setError('No se pudieron cargar los técnicos disponibles');
    } finally {
      setLoadingTechnicians(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedTechnician) {
      setError('Debe seleccionar un técnico');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Actualizar la orden de trabajo con el técnico asignado
      await apiClient.patch(`/v2/ordenes-trabajo/${maintenanceId}/`, {
        idtecnicoasignado: parseInt(selectedTechnician),
        observacionesfinales: notes || undefined
      });

      alert('Técnico asignado exitosamente');
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error al asignar técnico:', err);
      setError(err.response?.data?.message || 'Error al asignar el técnico');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setSelectedTechnician('');
      setEstimatedTime('');
      setNotes('');
      setError(null);
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Asignar Técnico"
      size="medium"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Información del reporte */}
        <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="flex-1">
              <div className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
                Reporte a Asignar
              </div>
              <div className="text-sm text-blue-800 dark:text-blue-200">
                {maintenanceTitle}
              </div>
            </div>
          </div>
        </div>

        {/* Selección de técnico */}
        <div>
          <Label htmlFor="technician" className="text-sm font-medium flex items-center gap-2">
            <User className="h-4 w-4" />
            Técnico *
          </Label>
          <Select
            value={selectedTechnician}
            onValueChange={setSelectedTechnician}
            disabled={loading || loadingTechnicians}
          >
            <SelectTrigger className="mt-1">
              <SelectValue placeholder={loadingTechnicians ? "Cargando técnicos..." : "Seleccionar técnico"} />
            </SelectTrigger>
            <SelectContent>
              {technicians.length === 0 && !loadingTechnicians && (
                <SelectItem value="no-technicians" disabled>
                  No hay técnicos disponibles
                </SelectItem>
              )}
              {technicians.map((tech) => (
                <SelectItem key={tech.idtecnico} value={tech.idtecnico.toString()}>
                  <div className="flex flex-col">
                    <span className="font-medium">{tech.nombre_completo}</span>
                    <span className="text-xs text-muted-foreground">
                      {tech.especialidades_list.length > 0 
                        ? tech.especialidades_list.join(', ')
                        : 'Sin especialidades'
                      } • {tech.ordenes_activas} OT activas
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Tiempo estimado */}
        <div>
          <Label htmlFor="estimatedTime" className="text-sm font-medium flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Tiempo Estimado (opcional)
          </Label>
          <Select
            value={estimatedTime}
            onValueChange={setEstimatedTime}
            disabled={loading}
          >
            <SelectTrigger className="mt-1">
              <SelectValue placeholder="Seleccionar tiempo estimado" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">1 hora</SelectItem>
              <SelectItem value="2">2 horas</SelectItem>
              <SelectItem value="3">3 horas</SelectItem>
              <SelectItem value="4">4 horas</SelectItem>
              <SelectItem value="6">6 horas</SelectItem>
              <SelectItem value="8">8 horas (1 día)</SelectItem>
              <SelectItem value="16">16 horas (2 días)</SelectItem>
              <SelectItem value="24">24 horas (3 días)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Notas adicionales */}
        <div>
          <Label htmlFor="notes" className="text-sm font-medium">
            Notas para el Técnico (opcional)
          </Label>
          <Textarea
            id="notes"
            placeholder="Instrucciones especiales, herramientas necesarias, etc."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            disabled={loading}
            rows={4}
            className="mt-1"
          />
        </div>

        {/* Botones */}
        <div className="flex gap-2 justify-end pt-4 border-t">
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
            disabled={loading || !selectedTechnician}
            className="min-w-[120px]"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Asignando...
              </>
            ) : (
              <>
                <User className="mr-2 h-4 w-4" />
                Asignar
              </>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default AssignTechnicianModal;
