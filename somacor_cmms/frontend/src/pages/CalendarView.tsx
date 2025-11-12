import React, { useState, useEffect } from 'react';
import { 
  Calendar as CalendarIcon, 
  Plus, 
  Filter, 
  ChevronLeft, 
  ChevronRight,
  Clock,
  Wrench,
  CheckCircle,
  AlertTriangle,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import CreateWorkOrderForm from '@/components/forms/CreateWorkOrderForm';
import { ordenesTrabajoServiceReal } from '@/services/apiServiceReal';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

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

interface CalendarStats {
  totalEventos: number;
  estaSemana: number;
  vencidos: number;
  completados: number;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

const CalendarView: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth());
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [stats, setStats] = useState<CalendarStats | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Datos de ejemplo para el diseño
  const mockEvents: CalendarEvent[] = [
    {
      id: '1',
      title: 'Mantenimiento Preventivo Compresor A-101',
      date: '2024-10-15',
      time: '08:00',
      type: 'preventivo',
      equipment: 'Compresor de Aire Principal',
      technician: 'Juan Pérez',
      status: 'programado',
      priority: 'media',
      description: 'Mantenimiento trimestral del compresor principal'
    },
    {
      id: '2',
      title: 'Reparación Bomba B-205',
      date: '2024-10-16',
      time: '10:30',
      type: 'correctivo',
      equipment: 'Bomba Centrífuga B-205',
      technician: 'María García',
      status: 'en_progreso',
      priority: 'alta',
      description: 'Cambio de sello mecánico y revisión de rodamientos'
    },
    {
      id: '3',
      title: 'Inspección Motor C-310',
      date: '2024-10-17',
      time: '14:00',
      type: 'inspeccion',
      equipment: 'Motor Eléctrico C-310',
      technician: 'Carlos López',
      status: 'programado',
      priority: 'baja',
      description: 'Inspección visual y medición de vibraciones'
    },
    {
      id: '4',
      title: 'Análisis Predictivo Válvula D-115',
      date: '2024-10-18',
      time: '09:15',
      type: 'predictivo',
      equipment: 'Válvula de Control D-115',
      technician: 'Ana Martínez',
      status: 'completado',
      priority: 'media',
      description: 'Análisis de tendencias y predicción de fallas'
    },
    {
      id: '5',
      title: 'Mantenimiento Urgente Motor E-420',
      date: '2024-10-19',
      time: '07:00',
      type: 'correctivo',
      equipment: 'Motor Eléctrico E-420',
      technician: 'Pedro Rodríguez',
      status: 'programado',
      priority: 'urgente',
      description: 'Falla en el sistema de refrigeración'
    }
  ];

  const mockStats: CalendarStats = {
    totalEventos: 45,
    estaSemana: 8,
    vencidos: 2,
    completados: 12
  };

  useEffect(() => {
    fetchCalendarData();
  }, []);

  const fetchCalendarData = async () => {
    try {
      // Cargar agendas desde el backend
      const response = await fetch('http://localhost:8000/api/v2/agendas/');
      const data = await response.json();
      const agendas = data.results || data || [];
      
      const eventosTransformados = agendas.map((agenda: any) => ({
        id: agenda.idagenda?.toString(),
        title: agenda.descripcion || 'Evento',
        date: agenda.fechaprogramada || new Date().toISOString().split('T')[0],
        time: agenda.horaprogramada || '00:00',
        type: 'preventivo',
        equipment: agenda.equipo_nombre || 'Sin equipo',
        technician: agenda.tecnico_nombre || 'Sin asignar',
        status: agenda.completado ? 'completado' : 'programado',
        priority: 'media',
        description: agenda.observaciones || ''
      }));
      
      setEvents(eventosTransformados);
      setStats({
        totalEventos: eventosTransformados.length,
        estaSemana: eventosTransformados.filter((e: any) => {
          const eventDate = new Date(e.date);
          const today = new Date();
          const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
          return eventDate >= today && eventDate <= weekFromNow;
        }).length,
        vencidos: 0,
        completados: eventosTransformados.filter((e: any) => e.status === 'completado').length
      });
      
      console.log('✅ Calendario cargado:', eventosTransformados.length);
    } catch (err) {
      console.warn('⚠️ API de calendario no disponible, mostrando vacío');
      setEvents([]);
      setStats({ totalEventos: 0, estaSemana: 0, vencidos: 0, completados: 0 });
    }
  };

  // Obtener eventos del mes actual
  const getCurrentMonthEvents = () => {
    return events.filter(event => {
      const eventDate = new Date(event.date);
      return eventDate.getMonth() === selectedMonth && 
             eventDate.getFullYear() === selectedYear;
    });
  };

  // Obtener eventos filtrados
  const getFilteredEvents = () => {
    let filtered = getCurrentMonthEvents();

    if (typeFilter !== 'all') {
      filtered = filtered.filter(event => event.type === typeFilter);
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(event => event.status === statusFilter);
    }

    return filtered;
  };

  // Generar días del mes
  const generateCalendarDays = () => {
    const firstDay = new Date(selectedYear, selectedMonth, 1);
    const lastDay = new Date(selectedYear, selectedMonth + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());

    const days = [];
    const current = new Date(startDate);

    for (let i = 0; i < 42; i++) {
      days.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }

    return days;
  };

  // Obtener eventos para un día específico
  const getEventsForDay = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return getFilteredEvents().filter(event => event.date === dateStr);
  };

  // Navegación del calendario
  const goToPreviousMonth = () => {
    if (selectedMonth === 0) {
      setSelectedMonth(11);
      setSelectedYear(selectedYear - 1);
    } else {
      setSelectedMonth(selectedMonth - 1);
    }
  };

  const goToNextMonth = () => {
    if (selectedMonth === 11) {
      setSelectedMonth(0);
      setSelectedYear(selectedYear + 1);
    } else {
      setSelectedMonth(selectedMonth + 1);
    }
  };

  const goToToday = () => {
    const today = new Date();
    setSelectedMonth(today.getMonth());
    setSelectedYear(today.getFullYear());
  };

  // Obtener badge de tipo
  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'preventivo':
        return <Badge variant="default" className="bg-blue-100 text-blue-800 hover:bg-blue-200">Preventivo</Badge>;
      case 'correctivo':
        return <Badge variant="default" className="bg-orange-100 text-orange-800 hover:bg-orange-200">Correctivo</Badge>;
      case 'predictivo':
        return <Badge variant="default" className="bg-green-100 text-green-800 hover:bg-green-200">Predictivo</Badge>;
      case 'inspeccion':
        return <Badge variant="default" className="bg-purple-100 text-purple-800 hover:bg-purple-200">Inspección</Badge>;
      default:
        return <Badge variant="secondary">{type}</Badge>;
    }
  };

  // Obtener badge de estado
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'programado':
        return <Badge variant="default" className="bg-yellow-100 text-yellow-800 hover:bg-yellow-200"><Clock className="h-3 w-3 mr-1" />Programado</Badge>;
      case 'en_progreso':
        return <Badge variant="default" className="bg-blue-100 text-blue-800 hover:bg-blue-200"><Wrench className="h-3 w-3 mr-1" />En Progreso</Badge>;
      case 'completado':
        return <Badge variant="default" className="bg-green-100 text-green-800 hover:bg-green-200"><CheckCircle className="h-3 w-3 mr-1" />Completado</Badge>;
      case 'cancelado':
        return <Badge variant="destructive"><AlertTriangle className="h-3 w-3 mr-1" />Cancelado</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
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

  const monthNames = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  const dayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];

  const calendarDays = generateCalendarDays();
  const filteredEvents = getFilteredEvents();

  return (
    <PageLayout>
      <PageHeader 
        title="Calendario de Mantenimiento" 
        subtitle="Programación y seguimiento de actividades de mantenimiento"
      >
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Evento
        </Button>
      </PageHeader>

      {/* Tarjetas de estadísticas */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Eventos</CardTitle>
            <CalendarIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalEventos}</div>
            <p className="text-xs text-muted-foreground">
              Eventos programados este mes
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Esta Semana</CardTitle>
            <Clock className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.estaSemana}</div>
            <p className="text-xs text-muted-foreground">
              Actividades programadas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vencidos</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{stats?.vencidos}</div>
            <p className="text-xs text-muted-foreground">
              Requieren atención urgente
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completados</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.completados}</div>
            <p className="text-xs text-muted-foreground">
              Actividades finalizadas
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Calendario y filtros */}
      <ContentGrid>
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
              <div>
                <CardTitle>Calendario de Actividades</CardTitle>
                <CardDescription>
                  Vista mensual de eventos de mantenimiento programados
                </CardDescription>
              </div>
              
              <div className="flex flex-col md:flex-row gap-2 w-full md:w-auto">
                <Select value={typeFilter} onValueChange={setTypeFilter}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Tipo de evento" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los tipos</SelectItem>
                    <SelectItem value="preventivo">Preventivo</SelectItem>
                    <SelectItem value="correctivo">Correctivo</SelectItem>
                    <SelectItem value="predictivo">Predictivo</SelectItem>
                    <SelectItem value="inspeccion">Inspección</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Estado" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los estados</SelectItem>
                    <SelectItem value="programado">Programado</SelectItem>
                    <SelectItem value="en_progreso">En Progreso</SelectItem>
                    <SelectItem value="completado">Completado</SelectItem>
                    <SelectItem value="cancelado">Cancelado</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {/* Navegación del calendario */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={goToPreviousMonth}>
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm" onClick={goToToday}>
                  Hoy
                </Button>
                <Button variant="outline" size="sm" onClick={goToNextMonth}>
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
              <h2 className="text-xl font-semibold">
                {monthNames[selectedMonth]} {selectedYear}
              </h2>
              <div className="w-32"></div>
                    </div>

            {/* Calendario */}
            <div className="grid grid-cols-7 gap-1 mb-4">
              {dayNames.map(day => (
                <div key={day} className="p-2 text-center font-medium text-sm text-muted-foreground">
                  {day}
                </div>
              ))}
            </div>

            <div className="grid grid-cols-7 gap-1">
              {calendarDays.map((day, index) => {
                const isCurrentMonth = day.getMonth() === selectedMonth;
                const isToday = day.toDateString() === new Date().toDateString();
                const dayEvents = getEventsForDay(day);

    return (
                  <div
                    key={index}
                    className={`min-h-[100px] p-2 border rounded-lg ${
                      isCurrentMonth ? 'bg-background' : 'bg-muted/30'
                    } ${isToday ? 'ring-2 ring-primary' : ''}`}
                  >
                    <div className={`text-sm font-medium mb-1 ${
                      isCurrentMonth ? 'text-foreground' : 'text-muted-foreground'
                    } ${isToday ? 'text-primary' : ''}`}>
                      {day.getDate()}
                    </div>
                    <div className="space-y-1">
                      {dayEvents.slice(0, 2).map(event => (
                        <div
                          key={event.id}
                          className="text-xs p-1 rounded bg-primary/10 text-primary truncate cursor-pointer hover:bg-primary/20"
                          title={event.title}
                        >
                          {event.time} - {event.title}
                        </div>
                      ))}
                      {dayEvents.length > 2 && (
                        <div className="text-xs text-muted-foreground">
                          +{dayEvents.length - 2} más
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Lista de eventos del mes */}
        <Card>
          <CardHeader>
            <CardTitle>Eventos de {monthNames[selectedMonth]}</CardTitle>
            <CardDescription>
              Lista detallada de actividades programadas
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredEvents.map(event => (
                <div key={event.id} className="border rounded-lg p-4 hover:bg-muted/50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-medium">{event.title}</h4>
                        {getTypeBadge(event.type)}
                        {getStatusBadge(event.status)}
                        {getPriorityBadge(event.priority)}
                      </div>
                      <div className="text-sm text-muted-foreground space-y-1">
                        <div className="flex items-center gap-2">
                          <Clock className="h-3 w-3" />
                          {event.date} a las {event.time}
                        </div>
                        <div className="flex items-center gap-2">
                          <Wrench className="h-3 w-3" />
                          {event.equipment}
                        </div>
                        <div className="flex items-center gap-2">
                          <CheckCircle className="h-3 w-3" />
                          {event.technician}
                        </div>
                        {event.description && (
                          <p className="text-xs mt-2">{event.description}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-1 ml-4">
                      <Button variant="outline" size="sm">
                        <Eye className="h-3 w-3" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Edit className="h-3 w-3" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              
              {filteredEvents.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <CalendarIcon className="mx-auto h-12 w-12 text-muted-foreground/50" />
                  <h3 className="mt-2 text-sm font-medium">No hay eventos</h3>
                  <p className="mt-1 text-sm">No se encontraron eventos para los filtros seleccionados.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </ContentGrid>

      {/* Formulario de creación de evento/orden de trabajo */}
      <CreateWorkOrderForm
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={() => {
          console.log('Evento/Orden de trabajo creado exitosamente');
        }}
      />
    </PageLayout>
    );
};

export default CalendarView;