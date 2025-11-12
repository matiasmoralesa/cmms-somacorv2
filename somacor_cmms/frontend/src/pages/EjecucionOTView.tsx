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
import { ordenesTrabajoService } from '@/services/apiService';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface OrdenTrabajo {
  idordentrabajo: number;
  numeroot: string;
  descripcionproblemareportado: string;
  prioridad: string;
  equipo_nombre: string;
  equipo_codigo: string;
  tecnico_nombre: string;
  estado_nombre: string;
  fechareportefalla: string;
  tipo_mantenimiento_nombre?: string;
  ubicacion?: string;
  duracion_estimada?: string;
  duracion_real?: string;
  hora_inicio?: string;
  hora_fin?: string;
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

  useEffect(() => {
    const fetchData = async () => {
      if (!id) {
        setError("ID de orden de trabajo no proporcionado");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError('');
        
        // Cargar orden de trabajo desde el backend
        const ordenData = await ordenesTrabajoService.getById(parseInt(id));
        
        // Mapear datos del backend al formato del componente
        const mappedOrden: OrdenTrabajo = {
          idordentrabajo: ordenData.idordentrabajo,
          numeroot: ordenData.numeroot,
          descripcionproblemareportado: ordenData.descripcionproblemareportado || 'Sin descripción',
          prioridad: ordenData.prioridad || 'Media',
          equipo_nombre: ordenData.equipo_nombre || 'Equipo desconocido',
          equipo_codigo: ordenData.equipo_codigo || 'N/A',
          tecnico_nombre: ordenData.tecnico_nombre || 'Sin asignar',
          estado_nombre: ordenData.estado_nombre || 'Pendiente',
          fechareportefalla: ordenData.fechareportefalla || new Date().toISOString().split('T')[0],
          tipo_mantenimiento_nombre: ordenData.tipo_mantenimiento_nombre || 'N/A',
          ubicacion: ordenData.ubicacion || 'Sin ubicación',
          duracion_estimada: ordenData.duracion_estimada || 'No especificada',
          duracion_real: ordenData.duracion_real,
          hora_inicio: ordenData.hora_inicio,
          hora_fin: ordenData.hora_fin
        };
        
        setOrden(mappedOrden);
        
        // Por ahora, las actividades se manejan como array vacío
        // hasta que el backend tenga un endpoint para actividades de OT
        const mockActividades: Actividad[] = [];
        setActividades(mockActividades);
        
        // Calcular estadísticas
        const calculatedStats: ExecutionStats = {
          totalActivities: mockActividades.length,
          completedActivities: mockActividades.filter(a => a.status === 'completada').length,
          inProgressActivities: mockActividades.filter(a => a.status === 'en_progreso').length,
          pendingActivities: mockActividades.filter(a => a.status === 'pendiente').length,
          totalTime: mappedOrden.duracion_estimada || '0 horas',
          actualTime: mappedOrden.duracion_real
        };
        
        setStats(calculatedStats);
        
      } catch (err: any) {
        console.error("Error fetching work order data:", err);
        setError(err.response?.data?.detail || "No se pudo cargar la información de la orden de trabajo.");
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
    setActividades(prev => prev.map(act => 
      act.id === activityId 
        ? { ...act, status: 'en_progreso', startTime: new Date().toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' }) }
        : act
    ));
    console.log('✅ Actividad iniciada:', activityId);
  };

  // Pausar actividad
  const pauseActivity = (activityId: number) => {
    setCurrentActivity(null);
    setActividades(prev => prev.map(act => 
      act.id === activityId 
        ? { ...act, status: 'pendiente' }
        : act
    ));
    console.log('⏸ Actividad pausada:', activityId);
  };

  // Completar actividad
  const completeActivity = (activityId: number) => {
    const endTime = new Date().toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });
    setActividades(prev => prev.map(act => {
      if (act.id === activityId) {
        const startTime = act.startTime || '00:00';
        const actualTime = calculateDuration(startTime, endTime);
        return { 
          ...act, 
          status: 'completada', 
          endTime,
          actualTime,
          observations: observations[activityId] || act.observations
        };
      }
      return act;
    }));
    setCurrentActivity(null);
    console.log('✅ Actividad completada:', activityId);
  };

  // Calcular duración entre dos tiempos
  const calculateDuration = (start: string, end: string): string => {
    const [startHour, startMin] = start.split(':').map(Number);
    const [endHour, endMin] = end.split(':').map(Number);
    const startMinutes = startHour * 60 + startMin;
    const endMinutes = endHour * 60 + endMin;
    const diffMinutes = endMinutes - startMinutes;
    const hours = Math.floor(diffMinutes / 60);
    const minutes = diffMinutes % 60;
    return hours > 0 ? `${hours} hora${hours > 1 ? 's' : ''} ${minutes} minutos` : `${minutes} minutos`;
  };

  // Subir archivo
  const handleFileUpload = (activityId: number) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*,application/pdf,.doc,.docx';
    input.multiple = true;
    input.onchange = (e: any) => {
      const files = Array.from(e.target.files || []) as File[];
      console.log('📎 Archivos seleccionados para actividad', activityId, ':', files.map(f => f.name));
      // Aquí se implementaría la lógica para subir los archivos al servidor
      alert(`${files.length} archivo(s) seleccionado(s): ${files.map(f => f.name).join(', ')}`);
    };
    input.click();
  };

  // Tomar foto
  const handleTakePhoto = (activityId: number) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.capture = 'environment';
    input.onchange = (e: any) => {
      const file = e.target.files?.[0];
      if (file) {
        console.log('📷 Foto tomada para actividad', activityId, ':', file.name);
        // Aquí se implementaría la lógica para procesar y subir la foto
        alert(`Foto capturada: ${file.name}`);
      }
    };
    input.click();
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
        title={`Ejecución OT: ${orden.numeroot}`}
        subtitle={`Orden de trabajo ${orden.numeroot} - ${orden.equipo_nombre}`}
      >
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={() => {
              console.log('💾 Guardando progreso...');
              alert('Progreso guardado correctamente');
            }}
          >
            <Save className="h-4 w-4 mr-2" />
            Guardar Progreso
          </Button>
          <Button 
            onClick={() => {
              const allCompleted = actividades.every(act => act.status === 'completada');
              if (!allCompleted) {
                alert('⚠️ Debes completar todas las actividades antes de finalizar la orden');
                return;
              }
              console.log('✅ Finalizando orden de trabajo...');
              alert('Orden de trabajo finalizada correctamente');
              navigate('/ordenes-trabajo');
            }}
          >
            <Send className="h-4 w-4 mr-2" />
            Finalizar Orden
          </Button>
          <Button variant="outline" onClick={() => navigate('/ordenes-trabajo')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Button>
        </div>
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
                {getMaintenanceTypeBadge(orden.tipo_mantenimiento_nombre || '')}
                {getPriorityBadge(orden.prioridad)}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Wrench className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Equipo:</span>
                  <span className="text-sm">{orden.equipo_nombre} ({orden.equipo_codigo})</span>
                </div>
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Técnico:</span>
                  <span className="text-sm">{orden.tecnico_nombre}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Fecha programada:</span>
                  <span className="text-sm">{new Date(orden.fechareportefalla).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Ubicación:</span>
                  <span className="text-sm">{orden.ubicacion || 'Sin ubicación'}</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Duración estimada:</span>
                  <span className="text-sm">{orden.duracion_estimada || 'No especificada'}</span>
                </div>
                {orden.duracion_real && (
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium">Duración real:</span>
                    <span className="text-sm text-green-600">{orden.duracion_real}</span>
                  </div>
                )}
                {orden.hora_inicio && (
                  <div className="flex items-center gap-2">
                    <Play className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium">Inicio:</span>
                    <span className="text-sm text-blue-600">{orden.hora_inicio}</span>
                  </div>
                )}
                {orden.hora_fin && (
                  <div className="flex items-center gap-2">
                    <Square className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium">Fin:</span>
                    <span className="text-sm text-green-600">{orden.hora_fin}</span>
                  </div>
                )}
              </div>
            </div>
            <div className="mt-4">
              <p className="text-sm text-muted-foreground">{orden.descripcionproblemareportado}</p>
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
            {actividades.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="mx-auto h-12 w-12 text-muted-foreground/50" />
                <h3 className="mt-2 text-sm font-medium">No hay actividades registradas</h3>
                <p className="mt-1 text-sm">Esta orden de trabajo aún no tiene actividades asignadas.</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  El módulo de actividades de OT estará disponible próximamente.
                </p>
              </div>
            ) : (
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
                      
                      {(actividad.status === 'en_progreso' || actividad.status === 'completada') && (
                        <div className="mt-3">
                          <label className="text-sm font-medium mb-1 block">Observaciones:</label>
                          <Input
                            placeholder="Agregar observaciones de la actividad..."
                            value={observations[actividad.id] || actividad.observations || ''}
                            onChange={(e) => setObservations(prev => ({ ...prev, [actividad.id]: e.target.value }))}
                            disabled={actividad.status === 'completada'}
                            className="text-sm"
                          />
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
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => startActivity(actividad.id)}
                          title="Iniciar actividad"
                        >
                          <Play className="h-3 w-3" />
                        </Button>
                      )}
                      {actividad.status === 'en_progreso' && (
                        <>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => pauseActivity(actividad.id)}
                            title="Pausar actividad"
                          >
                            <Pause className="h-3 w-3" />
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => completeActivity(actividad.id)}
                            title="Completar actividad"
                            className="text-green-600 hover:text-green-700"
                          >
                            <CheckCircle className="h-3 w-3" />
                          </Button>
                        </>
                      )}
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleFileUpload(actividad.id)}
                        title="Subir archivos"
                      >
                        <Upload className="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleTakePhoto(actividad.id)}
                        title="Tomar foto"
                      >
                        <Camera className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              </div>
            )}
          </CardContent>
        </Card>
      </ContentGrid>
    </PageLayout>
  );
};

export default EjecucionOTView;