import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Save, 
  Send, 
  Search, 
  Filter,
  Wrench,
  Clock,
  Calendar,
  User,
  CheckCircle,
  AlertTriangle,
  Plus,
  X,
  Upload,
  Camera
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface MaintenanceForm {
  id: number;
  equipmentName: string;
  equipmentCode: string;
  maintenanceType: 'preventivo' | 'correctivo' | 'predictivo';
  technician: string;
  scheduledDate: string;
  status: 'programado' | 'en_progreso' | 'completado' | 'cancelado';
  priority: 'baja' | 'media' | 'alta' | 'urgente';
  description: string;
  tasks: string[];
  estimatedDuration: string;
  actualDuration?: string;
  notes?: string;
  images?: string[];
  createdAt: string;
}

interface FormStats {
  totalForms: number;
  pendingForms: number;
  inProgressForms: number;
  completedForms: number;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

const MaintenanceFormView: React.FC = () => {
  const [forms, setForms] = useState<MaintenanceForm[]>([]);
  const [stats, setStats] = useState<FormStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [showNewForm, setShowNewForm] = useState(false);

  // Datos de ejemplo para el diseño
  const mockForms: MaintenanceForm[] = [
    {
      id: 1,
      equipmentName: 'Compresor de Aire Principal',
      equipmentCode: 'EQ-001',
      maintenanceType: 'preventivo',
      technician: 'Juan Pérez',
      scheduledDate: '2024-10-20',
      status: 'programado',
      priority: 'media',
      description: 'Mantenimiento preventivo trimestral del compresor principal',
      tasks: ['Cambio de filtros', 'Lubricación', 'Inspección visual'],
      estimatedDuration: '4 horas',
      createdAt: '2024-10-15'
    },
    {
      id: 2,
      equipmentName: 'Bomba Centrífuga B-205',
      equipmentCode: 'EQ-002',
      maintenanceType: 'correctivo',
      technician: 'María García',
      scheduledDate: '2024-10-18',
      status: 'en_progreso',
      priority: 'alta',
      description: 'Reparación de sello mecánico y revisión de rodamientos',
      tasks: ['Desmontaje de bomba', 'Cambio de sello', 'Revisión de rodamientos'],
      estimatedDuration: '6 horas',
      actualDuration: '3 horas',
      notes: 'Se encontró desgaste excesivo en los rodamientos',
      images: ['image1.jpg', 'image2.jpg'],
      createdAt: '2024-10-14'
    },
    {
      id: 3,
      equipmentName: 'Motor Eléctrico C-310',
      equipmentCode: 'EQ-003',
      maintenanceType: 'predictivo',
      technician: 'Carlos López',
      scheduledDate: '2024-10-22',
      status: 'completado',
      priority: 'baja',
      description: 'Análisis de vibraciones y medición de temperatura',
      tasks: ['Análisis de vibraciones', 'Medición de temperatura', 'Inspección de conexiones'],
      estimatedDuration: '2 horas',
      actualDuration: '2.5 horas',
      notes: 'Equipo en buen estado, continuar monitoreo',
      images: ['vibration_analysis.jpg'],
      createdAt: '2024-10-13'
    }
  ];

  const mockStats: FormStats = {
    totalForms: 15,
    pendingForms: 5,
    inProgressForms: 3,
    completedForms: 7
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Usar datos mock por ahora
        setForms(mockForms);
        setStats(mockStats);
        setError('');
      } catch (err) {
        console.error("Error fetching maintenance forms data:", err);
        setError("No se pudo cargar la información de formularios.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filtrar formularios
  const filteredForms = forms.filter(form => {
    const matchesSearch = form.equipmentName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         form.equipmentCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         form.technician.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || form.status === statusFilter;
    const matchesType = typeFilter === 'all' || form.maintenanceType === typeFilter;
    
    return matchesSearch && matchesStatus && matchesType;
  });

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

  // Obtener badge de estado
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'programado':
        return <Badge variant="default" className="bg-yellow-100 text-yellow-800"><Clock className="h-3 w-3 mr-1" />Programado</Badge>;
      case 'en_progreso':
        return <Badge variant="default" className="bg-blue-100 text-blue-800"><Wrench className="h-3 w-3 mr-1" />En Progreso</Badge>;
      case 'completado':
        return <Badge variant="default" className="bg-green-100 text-green-800"><CheckCircle className="h-3 w-3 mr-1" />Completado</Badge>;
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

  return (
    <PageLayout>
      <PageHeader 
        title="Formularios de Mantenimiento" 
        subtitle="Gestión y seguimiento de formularios de mantenimiento"
      >
        <Button onClick={() => setShowNewForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Formulario
        </Button>
      </PageHeader>

      {/* Tarjetas de estadísticas */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Formularios</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalForms}</div>
            <p className="text-xs text-muted-foreground">
              Formularios registrados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pendientes</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats?.pendingForms}</div>
            <p className="text-xs text-muted-foreground">
              Requieren atención
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">En Progreso</CardTitle>
            <Wrench className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.inProgressForms}</div>
            <p className="text-xs text-muted-foreground">
              Activamente en ejecución
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completados</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.completedForms}</div>
            <p className="text-xs text-muted-foreground">
              Finalizados exitosamente
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Lista de formularios */}
      <ContentGrid>
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
              <div>
                <CardTitle>Lista de Formularios</CardTitle>
                <CardDescription>
                  Formularios de mantenimiento y seguimiento de actividades
                </CardDescription>
              </div>
              
              <div className="flex flex-col md:flex-row gap-2 w-full md:w-auto">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar formulario..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-full md:w-64"
                  />
                </div>
                
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

                <Select value={typeFilter} onValueChange={setTypeFilter}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los tipos</SelectItem>
                    <SelectItem value="preventivo">Preventivo</SelectItem>
                    <SelectItem value="correctivo">Correctivo</SelectItem>
                    <SelectItem value="predictivo">Predictivo</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredForms.map(form => (
                <div key={form.id} className="border rounded-lg p-4 hover:bg-muted/50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-medium">{form.equipmentName}</h4>
                        <span className="text-sm text-muted-foreground">({form.equipmentCode})</span>
                        {getStatusBadge(form.status)}
                        {getMaintenanceTypeBadge(form.maintenanceType)}
                        {getPriorityBadge(form.priority)}
                      </div>
                      
                      <p className="text-sm text-muted-foreground mb-3">
                        {form.description}
                      </p>
                      
                      <div className="text-sm text-muted-foreground space-y-1">
                        <div className="flex items-center gap-2">
                          <User className="h-3 w-3" />
                          Técnico: {form.technician}
                        </div>
                        <div className="flex items-center gap-2">
                          <Calendar className="h-3 w-3" />
                          Fecha programada: {form.scheduledDate}
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="h-3 w-3" />
                          Duración estimada: {form.estimatedDuration}
                          {form.actualDuration && (
                            <span className="text-green-600">(Real: {form.actualDuration})</span>
                          )}
                        </div>
                        {form.images && form.images.length > 0 && (
                          <div className="flex items-center gap-2">
                            <Camera className="h-3 w-3" />
                            {form.images.length} imagen(es) adjunta(s)
                          </div>
                        )}
                      </div>
                      
                      <div className="mt-3">
                        <div className="flex items-center gap-2 mb-1">
                          <Wrench className="h-3 w-3 text-blue-600" />
                          <span className="text-sm font-medium text-blue-600">Tareas:</span>
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {form.tasks.map((task, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {task}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      
                      {form.notes && (
                        <div className="mt-3 p-2 bg-muted/50 rounded text-sm">
                          <strong>Notas:</strong> {form.notes}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex gap-1 ml-4">
                      <Button variant="outline" size="sm">
                        <FileText className="h-3 w-3" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Save className="h-3 w-3" />
                      </Button>
                      {form.status === 'programado' && (
                        <Button variant="outline" size="sm">
                          <Send className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {filteredForms.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <FileText className="mx-auto h-12 w-12 text-muted-foreground/50" />
                  <h3 className="mt-2 text-sm font-medium">No se encontraron formularios</h3>
                  <p className="mt-1 text-sm">No hay formularios que coincidan con los filtros seleccionados.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </ContentGrid>
    </PageLayout>
  );
};

export default MaintenanceFormView;