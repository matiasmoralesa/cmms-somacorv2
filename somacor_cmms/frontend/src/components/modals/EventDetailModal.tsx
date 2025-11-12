import React from 'react';
import { X, Calendar, Clock, Wrench, User, AlertCircle, FileText, MapPin } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Modal from '@/components/ui/Modal';

interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  time: string;
  type: 'preventivo' | 'correctivo' | 'predictivo' | 'inspeccion';
  equipment: string;
  technician: string;
  status: 'programado' | 'en_progreso' | 'completado' | 'cancelado';
  priority: 'baja' | 'media' | 'alta' | 'urgente';
  description?: string;
}

interface EventDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  event: CalendarEvent | null;
  onEdit?: (event: CalendarEvent) => void;
  onDelete?: (event: CalendarEvent) => void;
}

const EventDetailModal: React.FC<EventDetailModalProps> = ({
  isOpen,
  onClose,
  event,
  onEdit,
  onDelete
}) => {
  if (!event) return null;

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'preventivo':
        return <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-200">Preventivo</Badge>;
      case 'correctivo':
        return <Badge className="bg-orange-100 text-orange-800 hover:bg-orange-200">Correctivo</Badge>;
      case 'predictivo':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-200">Predictivo</Badge>;
      case 'inspeccion':
        return <Badge className="bg-purple-100 text-purple-800 hover:bg-purple-200">Inspección</Badge>;
      default:
        return <Badge variant="secondary">{type}</Badge>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'programado':
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-200">Programado</Badge>;
      case 'en_progreso':
        return <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-200">En Progreso</Badge>;
      case 'completado':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-200">Completado</Badge>;
      case 'cancelado':
        return <Badge variant="destructive">Cancelado</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

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
      title="Detalles del Evento"
      size="large"
    >
      <div className="space-y-6">
        {/* Título y badges */}
        <div>
          <h3 className="text-xl font-semibold mb-3">{event.title}</h3>
          <div className="flex flex-wrap gap-2">
            {getTypeBadge(event.type)}
            {getStatusBadge(event.status)}
            {getPriorityBadge(event.priority)}
          </div>
        </div>

        {/* Información principal */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Fecha */}
          <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
            <Calendar className="h-5 w-5 text-primary mt-0.5" />
            <div>
              <div className="text-sm font-medium text-muted-foreground">Fecha</div>
              <div className="text-base font-medium capitalize">{formatDate(event.date)}</div>
            </div>
          </div>

          {/* Hora */}
          <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
            <Clock className="h-5 w-5 text-primary mt-0.5" />
            <div>
              <div className="text-sm font-medium text-muted-foreground">Hora</div>
              <div className="text-base font-medium">{event.time}</div>
            </div>
          </div>

          {/* Equipo */}
          <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
            <Wrench className="h-5 w-5 text-primary mt-0.5" />
            <div>
              <div className="text-sm font-medium text-muted-foreground">Equipo</div>
              <div className="text-base font-medium">{event.equipment}</div>
            </div>
          </div>

          {/* Técnico */}
          <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
            <User className="h-5 w-5 text-primary mt-0.5" />
            <div>
              <div className="text-sm font-medium text-muted-foreground">Técnico Asignado</div>
              <div className="text-base font-medium">{event.technician}</div>
            </div>
          </div>
        </div>

        {/* Descripción */}
        {event.description && (
          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="flex items-start gap-3">
              <FileText className="h-5 w-5 text-primary mt-0.5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-muted-foreground mb-2">Descripción</div>
                <p className="text-sm text-foreground leading-relaxed">{event.description}</p>
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
                Información del Evento
              </div>
              <div className="text-sm text-blue-800 dark:text-blue-200">
                ID de Orden: {event.id}
              </div>
            </div>
          </div>
        </div>

        {/* Botones de acción */}
        <div className="flex gap-2 justify-end pt-4 border-t">
          <Button variant="outline" onClick={onClose}>
            Cerrar
          </Button>
          {onEdit && (
            <Button variant="default" onClick={() => onEdit(event)}>
              Editar Evento
            </Button>
          )}
          {onDelete && event.status !== 'completado' && (
            <Button variant="destructive" onClick={() => onDelete(event)}>
              Cancelar Evento
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
};

export default EventDetailModal;
