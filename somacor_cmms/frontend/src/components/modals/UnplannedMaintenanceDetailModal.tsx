import React from 'react';
import { X, Calendar, Clock, Wrench, User, AlertCircle, FileText, MapPin, Camera } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Modal from '@/components/ui/Modal';

interface UnplannedMaintenance {
  id: string;
  title: string;
  equipment: string;
  equipmentCode: string;
  reportedBy: string;
  reportedDate: string;
  priority: 'baja' | 'media' | 'alta' | 'urgente';
  status: 'reportado' | 'en_revision' | 'asignado' | 'en_progreso' | 'completado' | 'cancelado';
  description: string;
  location: string;
  estimatedTime?: string;
  assignedTo?: string;
  images?: string[];
}

interface UnplannedMaintenanceDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  maintenance: UnplannedMaintenance | null;
  onEdit?: (maintenance: UnplannedMaintenance) => void;
  onAssign?: (maintenance: UnplannedMaintenance) => void;
}

const UnplannedMaintenanceDetailModal: React.FC<UnplannedMaintenanceDetailModalProps> = ({
  isOpen,
  onClose,
  maintenance,
  onEdit,
  onAssign
}) => {
  if (!maintenance) return null;

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'baja':
        return <Badge variant="secondary">Baja</Badge>;
      case 'media':
        return <Badge className="bg-blue-100 text-blue-800">Media</Badge>;
      case 'alta':
        return <Badge className="bg-orange-100 text-orange-800">Alta</Badge>;
      case 'urgente':
        return <Badge variant="destructive">Urgente</Badge>;
      default:
        return <Badge variant="secondary">{priority}</Badge>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'reportado':
        return <Badge className="bg-yellow-100 text-yellow-800">Reportado</Badge>;
      case 'en_revision':
        return <Badge className="bg-blue-100 text-blue-800">En Revisión</Badge>;
      case 'asignado':
        return <Badge className="bg-purple-100 text-purple-800">Asignado</Badge>;
      case 'en_progreso':
        return <Badge className="bg-blue-100 text-blue-800">En Progreso</Badge>;
      case 'completado':
        return <Badge className="bg-green-100 text-green-800">Completado</Badge>;
      case 'cancelado':
        return <Badge variant="destructive">Cancelado</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-CL', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalles del Reporte"
      size="large"
    >
      <div className="space-y-6">
        {/* Título y badges */}
        <div>
          <h3 className="text-xl font-semibold mb-3">{maintenance.title}</h3>
          <div className="flex flex-wrap gap-2">
            {getPriorityBadge(maintenance.priority)}
            {getStatusBadge(maintenance.status)}
          </div>
        </div>

        {/* Información principal */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Equipo */}
          <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
            <Wrench className="h-5 w-5 text-primary mt-0.5" />
            <div>
              <div className="text-sm font-medium text-muted-foreground">Equipo</div>
              <div className="text-base font-medium">{maintenance.equipment}</div>
              <div className="text-sm text-muted-foreground">{maintenance.equipmentCode}</div>
            </div>
          </div>

          {/* Reportado por */}
          <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
            <User className="h-5 w-5 text-primary mt-0.5" />
            <div>
              <div className="text-sm font-medium text-muted-foreground">Reportado por</div>
              <div className="text-base font-medium">{maintenance.reportedBy}</div>
            </div>
          </div>

          {/* Fecha de reporte */}
          <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
            <Calendar className="h-5 w-5 text-primary mt-0.5" />
            <div>
              <div className="text-sm font-medium text-muted-foreground">Fecha de Reporte</div>
              <div className="text-base font-medium capitalize">{formatDate(maintenance.reportedDate)}</div>
            </div>
          </div>

          {/* Ubicación */}
          <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
            <MapPin className="h-5 w-5 text-primary mt-0.5" />
            <div>
              <div className="text-sm font-medium text-muted-foreground">Ubicación</div>
              <div className="text-base font-medium">{maintenance.location}</div>
            </div>
          </div>

          {/* Técnico asignado */}
          {maintenance.assignedTo && (
            <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
              <User className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <div className="text-sm font-medium text-muted-foreground">Asignado a</div>
                <div className="text-base font-medium">{maintenance.assignedTo}</div>
              </div>
            </div>
          )}

          {/* Tiempo estimado */}
          {maintenance.estimatedTime && (
            <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
              <Clock className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <div className="text-sm font-medium text-muted-foreground">Tiempo Estimado</div>
                <div className="text-base font-medium">{maintenance.estimatedTime}</div>
              </div>
            </div>
          )}
        </div>

        {/* Descripción */}
        <div className="p-4 bg-muted/50 rounded-lg">
          <div className="flex items-start gap-3">
            <FileText className="h-5 w-5 text-primary mt-0.5" />
            <div className="flex-1">
              <div className="text-sm font-medium text-muted-foreground mb-2">Descripción del Problema</div>
              <p className="text-sm text-foreground leading-relaxed">{maintenance.description}</p>
            </div>
          </div>
        </div>

        {/* Imágenes */}
        {maintenance.images && maintenance.images.length > 0 && (
          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="flex items-start gap-3">
              <Camera className="h-5 w-5 text-primary mt-0.5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-muted-foreground mb-2">
                  Imágenes Adjuntas ({maintenance.images.length})
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {maintenance.images.map((image, index) => (
                    <div key={index} className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                      <Camera className="h-8 w-8 text-muted-foreground" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Información adicional */}
        <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="flex-1">
              <div className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
                Información del Reporte
              </div>
              <div className="text-sm text-blue-800 dark:text-blue-200">
                ID de Reporte: {maintenance.id}
              </div>
            </div>
          </div>
        </div>

        {/* Botones de acción */}
        <div className="flex gap-2 justify-end pt-4 border-t">
          <Button variant="outline" onClick={onClose}>
            Cerrar
          </Button>
          {onEdit && maintenance.status !== 'completado' && (
            <Button variant="default" onClick={() => onEdit(maintenance)}>
              Editar Reporte
            </Button>
          )}
          {onAssign && maintenance.status === 'reportado' && (
            <Button variant="default" onClick={() => onAssign(maintenance)}>
              Asignar Técnico
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
};

export default UnplannedMaintenanceDetailModal;
