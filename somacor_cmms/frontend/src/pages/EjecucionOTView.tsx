import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Clock, 
  User, 
  Wrench, 
  CheckCircle, 
  AlertTriangle,
  FileText,
  Play,
  Pause,
  Square,
  Save,
  Upload,
  Camera,
  Calendar,
  MapPin,
  Settings,
  Send
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface OrdenTrabajo {
  id: string;
  title: string;
  equipment: string;
  equipmentCode: string;
  type: 'preventivo' | 'correctivo' | 'predictivo';
  priority: 'baja' | 'media' | 'alta' | 'urgente';
  status: 'programado' | 'en_progreso' | 'completado' | 'cancelado';
  assignedTo: string;
  scheduledDate: string;
  description: string;
  location: string;
  estimatedDuration: string;
  actualDuration?: string;
  startTime?: string;
  endTime?: string;
}

interface Actividad {
  id: number;
  name: string;
  description: string;
  status: 'pendiente' | 'en_progreso' | 'completada' | 'cancelada';
  estimatedTime: string;
  actualTime?: string;
  startTime?: string;
  endTime?: string;
  observations?: string;
  measurements?: { parameter: string; value: string; unit: string }[];
  images?: string[];
}

interface ExecutionStats {
  totalActivities: number;
  completedActivities: number;
  inProgressActivities: number;
  pendingActivities: number;
  totalTime: string;
  actualTime?: string;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

const EjecucionOTView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [orden, setOrden] = useState<OrdenTrabajo | null>(null);
  const [actividades, setActividades] = useState<Actividad[]>([]);
  const [stats, setStats] = useState<ExecutionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentActivity, setCurrentActivity] = useState<number | null>(null);
  const [observations, setObservations] = useState<Record<number, string>>({});

  // Datos de ejemplo para el diseño
  const mockOrden: OrdenTrabajo = {
    id: id || '1',
    title: 'Mantenimiento Preventivo Compresor A-101',
    equipment: 'Compresor de Aire Principal',
    equipmentCode: 'EQ-001',
    type: 'preventivo',
    priority: 'media',
    status: 'en_progreso',
    assignedTo: 'Juan Pérez',
    scheduledDate: '2024-10-20',
    description: 'Mantenimiento preventivo trimestral del compresor principal incluyendo cambio de filtros, lubricación e inspección visual',
    location: 'Planta Norte - Sector A',
    estimatedDuration: '4 horas',
    actualDuration: '2.5 horas',
    startTime: '08:00',
    endTime: '10:30'
  };

  const mockActividades: Actividad[] = [
    {
      id: 1,
      name: 'Cambio de Filtros',
      description: 'Reemplazo de filtros de aire, aceite y combustible',
      status: 'completada',
      estimatedTime: '1 hora',
      actualTime: '45 minutos',
      startTime: '08:00',
      endTime: '08:45',
      observations: 'Filtros en buen estado, reemplazo preventivo realizado',
      measurements: [
        { parameter: 'Presión de aire', value: '7.2', unit: 'bar' },
        { parameter: 'Temperatura', value: '65', unit: '°C' }
      ],
      images: ['filtro_antes.jpg', 'filtro_despues.jpg']
    },
    {
      id: 2,
      name: 'Lubricación',
      description: 'Lubricación de componentes móviles y verificación de niveles',
      status: 'en_progreso',
      estimatedTime: '1.5 horas',
      startTime: '08:45',
      observations: 'Iniciando lubricación de rodamientos principales'
    },
    {
      id: 3,
      name: 'Inspección Visual',
      description: 'Inspección visual general del equipo y componentes',
      status: 'pendiente',
      estimatedTime: '1.5 horas'
    }
  ];

  const mockStats: ExecutionStats = {
    totalActivities: 3,
    completedActivities: 1,
    inProgressActivities: 1,
    pendingActivities: 1,
    totalTime: '4 horas',
    actualTime: '2.5 horas'
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Usar datos mock por ahora
        setOrden(mockOrden);
        setActividades(mockActividades);
        setStats(mockStats);
        setError('');
      } catch (err) {
        console.error("Error fetching work order data:", err);
        setError("No se pudo cargar la información de la orden de trabajo.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  // Obtener badge de estado de actividad
  const getActivityStatusBadge = (status: string) => {
    switch (status) {
      case 'pendiente':
        return <Badge variant="secondary"><Clock className="h-3 w-3 mr-1" />Pendiente</Badge>;
      case 'en_progreso':
        return <Badge variant="default" className="bg-blue-100 text-blue-800"><Play className="h-3 w-3 mr-1" />En Progreso</Badge>;
      case 'completada':
        return <Badge variant="default" className="bg-green-100 text-green-800"><CheckCircle className="h-3 w-3 mr-1" />Completada</Badge>;
      case 'cancelada':
        return <Badge variant="destructive"><AlertTriangle className="h-3 w-3 mr-1" />Cancelada</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  // Obtener badge de tipo de mantenimiento
  const getMaintenanceTypeBadge = (type: string) => {
    switch (type) {
      case 'preventivo':
        return <Badge variant="default" className="bg-blue-100 text-blue-800">Preventivo</Badge>;
      case 'correctivo':
        return <Badge variant="default" className="bg-orange-100 text-orange-800">Correctivo</Badge>;
      case 'predictivo':
        return <Badge variant="default" className="bg-green-100 text-green-800">Predictivo</Badge>;
      default:
        return <Badge variant="secondary">{type}</Badge>;
    }
  };

  // Obtener badge de prioridad
  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'baja':
        return <Badge variant="secondary">Baja</Badge>;
      case 'media':
        return <Badge variant="default" className="bg-blue-100 text-blue-800">Media</Badge>;
      case 'alta':
        return <Badge variant="default" className="bg-orange-100 text-orange-800">Alta</Badge>;
      case 'urgente':
        return <Badge variant="destructive">Urgente</Badge>;
      default:
        return <Badge variant="secondary">{priority}</Badge>;
    }
  };

  // Iniciar actividad
  const startActivity = (activityId: number) => {
    setCurrentActivity(activityId);
    // Aquí se implementaría la lógica para iniciar el cronómetro
  };

  // Pausar actividad
  const pauseActivity = (activityId: number) => {
    setCurrentActivity(null);
    // Aquí se implementaría la lógica para pausar el cronómetro
  };

  // Completar actividad
  const completeActivity = (activityId: number) => {
    // Aquí se implementaría la lógica para completar la actividad
    console.log('Completando actividad:', activityId);
  };

  if (loading) {
    return (
      <PageLayout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout>
        <div className="p-8 text-center text-destructive bg-destructive/10 rounded-lg">
          {error}
        </div>
      </PageLayout>
    );
  }

  if (!orden) {
    return (
      <PageLayout>
        <div className="p-8 text-center text-muted-foreground">
          <AlertTriangle className="mx-auto h-12 w-12 text-muted-foreground/50" />
          <h3 className="mt-2 text-sm font-medium">Orden de trabajo no encontrada</h3>
          <p className="mt-1 text-sm">La orden de trabajo solicitada no existe o no está disponible.</p>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader 
        title={`Ejecución OT: ${orden.title}`}
        subtitle={`Orden de trabajo ${orden.id} - ${orden.equipment}`}
      >
        <Button variant="outline" onClick={() => navigate('/ordenes-trabajo')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Volver
        </Button>
      </PageHeader>

      {/* Información de la orden */}
      <ContentGrid>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Información de la Orden</CardTitle>
                <CardDescription>
                  Detalles de la orden de trabajo en ejecución
                </CardDescription>
              </div>
              <div className="flex gap-2">
                {getMaintenanceTypeBadge(orden.type)}
                {getPriorityBadge(orden.priority)}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Wrench className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Equipo:</span>
                  <span className="text-sm">{orden.equipment} ({orden.equipmentCode})</span>
                </div>
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Técnico:</span>
                  <span className="text-sm">{orden.assignedTo}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Fecha programada:</span>
                  <span className="text-sm">{orden.scheduledDate}</span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Ubicación:</span>
                  <span className="text-sm">{orden.location}</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Duración estimada:</span>
                  <span className="text-sm">{orden.estimatedDuration}</span>
                </div>
                {orden.actualDuration && (
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium">Duración real:</span>
                    <span className="text-sm text-green-600">{orden.actualDuration}</span>
                  </div>
                )}
                {orden.startTime && (
                  <div className="flex items-center gap-2">
                    <Play className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium">Inicio:</span>
                    <span className="text-sm text-blue-600">{orden.startTime}</span>
                  </div>
                )}
                {orden.endTime && (
                  <div className="flex items-center gap-2">
                    <Square className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium">Fin:</span>
                    <span className="text-sm text-green-600">{orden.endTime}</span>
                  </div>
                )}
              </div>
            </div>
            <div className="mt-4">
              <p className="text-sm text-muted-foreground">{orden.description}</p>
            </div>
          </CardContent>
        </Card>
      </ContentGrid>

      {/* Estadísticas de ejecución */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Actividades</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalActivities}</div>
            <p className="text-xs text-muted-foreground">
              Actividades programadas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completadas</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.completedActivities}</div>
            <p className="text-xs text-muted-foreground">
              {stats ? Math.round((stats.completedActivities / stats.totalActivities) * 100) : 0}% del total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">En Progreso</CardTitle>
            <Play className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.inProgressActivities}</div>
            <p className="text-xs text-muted-foreground">
              Activamente en ejecución
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tiempo Real</CardTitle>
            <Clock className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{stats?.actualTime || '0:00'}</div>
            <p className="text-xs text-muted-foreground">
              Tiempo transcurrido
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Lista de actividades */}
      <ContentGrid>
        <Card>
          <CardHeader>
            <CardTitle>Actividades de Mantenimiento</CardTitle>
            <CardDescription>
              Lista de actividades a ejecutar en esta orden de trabajo
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {actividades.map(actividad => (
                <div key={actividad.id} className="border rounded-lg p-4 hover:bg-muted/50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-medium">{actividad.name}</h4>
                        {getActivityStatusBadge(actividad.status)}
                      </div>
                      
                      <p className="text-sm text-muted-foreground mb-3">
                        {actividad.description}
                      </p>
                      
                      <div className="text-sm text-muted-foreground space-y-1">
                        <div className="flex items-center gap-2">
                          <Clock className="h-3 w-3" />
                          Tiempo estimado: {actividad.estimatedTime}
                          {actividad.actualTime && (
                            <span className="text-green-600">(Real: {actividad.actualTime})</span>
                          )}
                        </div>
                        {actividad.startTime && (
                          <div className="flex items-center gap-2">
                            <Play className="h-3 w-3 text-blue-600" />
                            Inicio: {actividad.startTime}
                          </div>
                        )}
                        {actividad.endTime && (
                          <div className="flex items-center gap-2">
                            <Square className="h-3 w-3 text-green-600" />
                            Fin: {actividad.endTime}
                          </div>
                        )}
                      </div>
                      
                      {actividad.observations && (
                        <div className="mt-3 p-2 bg-muted/50 rounded text-sm">
                          <strong>Observaciones:</strong> {actividad.observations}
                        </div>
                      )}
                      
                      {actividad.measurements && actividad.measurements.length > 0 && (
                        <div className="mt-3">
                          <div className="flex items-center gap-2 mb-1">
                            <Settings className="h-3 w-3 text-blue-600" />
                            <span className="text-sm font-medium text-blue-600">Mediciones:</span>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {actividad.measurements.map((measurement, index) => (
                              <div key={index} className="text-sm bg-muted/30 p-2 rounded">
                                <strong>{measurement.parameter}:</strong> {measurement.value} {measurement.unit}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {actividad.images && actividad.images.length > 0 && (
                        <div className="mt-3">
                          <div className="flex items-center gap-2 mb-1">
                            <Camera className="h-3 w-3 text-purple-600" />
                            <span className="text-sm font-medium text-purple-600">Imágenes:</span>
                          </div>
                          <div className="flex gap-2">
                            {actividad.images.map((image, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {image}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex gap-1 ml-4">
                      {actividad.status === 'pendiente' && (
                        <Button variant="outline" size="sm" onClick={() => startActivity(actividad.id)}>
                          <Play className="h-3 w-3" />
                        </Button>
                      )}
                      {actividad.status === 'en_progreso' && (
                        <>
                          <Button variant="outline" size="sm" onClick={() => pauseActivity(actividad.id)}>
                            <Pause className="h-3 w-3" />
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => completeActivity(actividad.id)}>
                            <CheckCircle className="h-3 w-3" />
                          </Button>
                        </>
                      )}
                      <Button variant="outline" size="sm">
                        <Upload className="h-3 w-3" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Camera className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </ContentGrid>
    </PageLayout>
  );
};

export default EjecucionOTView;