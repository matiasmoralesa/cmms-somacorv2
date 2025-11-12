import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Plus, 
  Search, 
  Filter,
  Wrench,
  Clock,
  Calendar,
  CheckCircle,
  AlertTriangle,
  Edit,
  Trash2,
  Eye,
  Save,
  RefreshCw,
  Bell,
  FileText
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

interface MaintenanceConfig {
  id: number;
  equipmentName: string;
  equipmentCode: string;
  maintenanceType: 'preventivo' | 'correctivo' | 'predictivo';
  frequency: string;
  nextMaintenance: string;
  isActive: boolean;
  tasks: string[];
  estimatedDuration: string;
  assignedTechnician: string;
  priority: 'baja' | 'media' | 'alta' | 'urgente';
  createdAt: string;
  lastUpdated: string;
}

interface ConfigStats {
  totalConfigs: number;
  activeConfigs: number;
  preventiveConfigs: number;
  nextMaintenances: number;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

const MaintenanceConfigView: React.FC = () => {
  const [configs, setConfigs] = useState<MaintenanceConfig[]>([]);
  const [stats, setStats] = useState<ConfigStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedConfig, setSelectedConfig] = useState<MaintenanceConfig | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDetailPanel, setShowDetailPanel] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  // Datos de ejemplo para el diseño
  const mockConfigs: MaintenanceConfig[] = [
    {
      id: 1,
      equipmentName: 'Compresor de Aire Principal',
      equipmentCode: 'EQ-001',
      maintenanceType: 'preventivo',
      frequency: 'Mensual',
      nextMaintenance: '2024-11-15',
      isActive: true,
      tasks: ['Cambio de filtros', 'Lubricación', 'Inspección visual'],
      estimatedDuration: '4 horas',
      assignedTechnician: 'Juan Pérez',
      priority: 'media',
      createdAt: '2024-01-15',
      lastUpdated: '2024-10-15'
    },
    {
      id: 2,
      equipmentName: 'Bomba Centrífuga B-205',
      equipmentCode: 'EQ-002',
      maintenanceType: 'preventivo',
      frequency: 'Bimensual',
      nextMaintenance: '2024-11-20',
      isActive: true,
      tasks: ['Revisión de rodamientos', 'Cambio de aceite', 'Prueba de funcionamiento'],
      estimatedDuration: '3 horas',
      assignedTechnician: 'María García',
      priority: 'alta',
      createdAt: '2024-02-20',
      lastUpdated: '2024-10-14'
    },
    {
      id: 3,
      equipmentName: 'Motor Eléctrico C-310',
      equipmentCode: 'EQ-003',
      maintenanceType: 'predictivo',
      frequency: 'Trimestral',
      nextMaintenance: '2024-12-10',
      isActive: true,
      tasks: ['Análisis de vibraciones', 'Medición de temperatura', 'Inspección de conexiones'],
      estimatedDuration: '2 horas',
      assignedTechnician: 'Carlos López',
      priority: 'baja',
      createdAt: '2024-03-10',
      lastUpdated: '2024-10-13'
    },
    {
      id: 4,
      equipmentName: 'Válvula de Control D-115',
      equipmentCode: 'EQ-004',
      maintenanceType: 'correctivo',
      frequency: 'Según necesidad',
      nextMaintenance: '2024-10-25',
      isActive: false,
      tasks: ['Reparación de actuador', 'Calibración', 'Prueba de sellado'],
      estimatedDuration: '6 horas',
      assignedTechnician: 'Ana Martínez',
      priority: 'urgente',
      createdAt: '2024-04-15',
      lastUpdated: '2024-10-12'
    }
  ];

  const mockStats: ConfigStats = {
    totalConfigs: 24,
    activeConfigs: 20,
    preventiveConfigs: 18,
    nextMaintenances: 8
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Usar datos mock por ahora
        setConfigs(mockConfigs);
        setStats(mockStats);
        setError('');
      } catch (err) {
        console.error("Error fetching maintenance configs data:", err);
        setError("No se pudo cargar la información de configuraciones.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filtrar configuraciones
  const filteredConfigs = configs.filter(config => {
    const matchesSearch = config.equipmentName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         config.equipmentCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         config.assignedTechnician.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = typeFilter === 'all' || config.maintenanceType === typeFilter;
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'active' && config.isActive) ||
                         (statusFilter === 'inactive' && !config.isActive);
    
    return matchesSearch && matchesType && matchesStatus;
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

  // Obtener badge de estado
  const getStatusBadge = (isActive: boolean) => {
    return isActive ? (
      <Badge variant="default" className="bg-green-100 text-green-800">
        <CheckCircle className="h-3 w-3 mr-1" />Activo
      </Badge>
    ) : (
      <Badge variant="destructive">
        <AlertTriangle className="h-3 w-3 mr-1" />Inactivo
      </Badge>
    );
  };

  // Handlers de botones
  const handleCreateConfig = () => {
    console.log('✅ Abriendo formulario de nueva configuración');
    setShowCreateForm(true);
    alert('Formulario de nueva configuración (por implementar)');
  };

  const handleViewConfig = (config: MaintenanceConfig) => {
    console.log('👁️ Viendo configuración:', config.equipmentName);
    setSelectedConfig(config);
    setShowDetailPanel(true);
    alert(`Ver detalles de: ${config.equipmentName}`);
  };

  const handleEditConfig = (config: MaintenanceConfig) => {
    console.log('✏️ Editando configuración:', config.equipmentName);
    setSelectedConfig(config);
    setShowEditForm(true);
    alert(`Editar configuración de: ${config.equipmentName}`);
  };

  const handleRefreshConfig = (config: MaintenanceConfig) => {
    console.log('🔄 Actualizando configuración:', config.equipmentName);
    alert(`Actualizar próximo mantenimiento de: ${config.equipmentName}`);
  };

  const handleDeleteConfig = (config: MaintenanceConfig) => {
    console.log('🗑️ Eliminando configuración:', config.equipmentName);
    setSelectedConfig(config);
    if (confirm(`¿Estás seguro de eliminar la configuración de ${config.equipmentName}?`)) {
      setConfigs(prev => prev.filter(c => c.id !== config.id));
      alert('Configuración eliminada correctamente');
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
        title="Configuración de Mantenimiento" 
        subtitle="Gestión de planes y configuraciones de mantenimiento preventivo"
      >
        <Button onClick={handleCreateConfig}>
          <Plus className="h-4 w-4 mr-2" />
          Nueva Configuración
        </Button>
      </PageHeader>

      {/* Tarjetas de estadísticas */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Configuraciones</CardTitle>
            <Settings className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalConfigs}</div>
            <p className="text-xs text-muted-foreground">
              Planes configurados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Configuraciones Activas</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.activeConfigs}</div>
            <p className="text-xs text-muted-foreground">
              {stats ? Math.round((stats.activeConfigs / stats.totalConfigs) * 100) : 0}% del total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Preventivos</CardTitle>
            <Wrench className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.preventiveConfigs}</div>
            <p className="text-xs text-muted-foreground">
              Mantenimientos preventivos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Próximos Mantenimientos</CardTitle>
            <Bell className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats?.nextMaintenances}</div>
            <p className="text-xs text-muted-foreground">
              Esta semana
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Lista de configuraciones */}
      <ContentGrid>
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
              <div>
                <CardTitle>Configuraciones de Mantenimiento</CardTitle>
                <CardDescription>
                  Planes y configuraciones de mantenimiento por equipo
                </CardDescription>
              </div>
              
              <div className="flex flex-col md:flex-row gap-2 w-full md:w-auto">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar configuración..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-full md:w-64"
                  />
                </div>
                
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

                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Estado" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los estados</SelectItem>
                    <SelectItem value="active">Activos</SelectItem>
                    <SelectItem value="inactive">Inactivos</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredConfigs.map(config => (
                <div key={config.id} className="border rounded-lg p-4 hover:bg-muted/50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-medium">{config.equipmentName}</h4>
                        <span className="text-sm text-muted-foreground">({config.equipmentCode})</span>
                        {getStatusBadge(config.isActive)}
                        {getMaintenanceTypeBadge(config.maintenanceType)}
                        {getPriorityBadge(config.priority)}
                      </div>
                      
                      <div className="text-sm text-muted-foreground space-y-1">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-3 w-3" />
                          Próximo mantenimiento: {config.nextMaintenance}
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="h-3 w-3" />
                          Frecuencia: {config.frequency}
                        </div>
                        <div className="flex items-center gap-2">
                          <Wrench className="h-3 w-3" />
                          Duración estimada: {config.estimatedDuration}
                        </div>
                        <div className="flex items-center gap-2">
                          <CheckCircle className="h-3 w-3" />
                          Técnico asignado: {config.assignedTechnician}
                        </div>
                      </div>
                      
                      <div className="mt-3">
                        <div className="flex items-center gap-2 mb-1">
                          <FileText className="h-3 w-3 text-blue-600" />
                          <span className="text-sm font-medium text-blue-600">Tareas:</span>
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {config.tasks.map((task, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {task}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-1 ml-4">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleViewConfig(config)}
                        title="Ver detalles"
                      >
                        <Eye className="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleEditConfig(config)}
                        title="Editar configuración"
                      >
                        <Edit className="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleRefreshConfig(config)}
                        title="Actualizar próximo mantenimiento"
                      >
                        <RefreshCw className="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDeleteConfig(config)}
                        title="Eliminar configuración"
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              
              {filteredConfigs.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Settings className="mx-auto h-12 w-12 text-muted-foreground/50" />
                  <h3 className="mt-2 text-sm font-medium">No se encontraron configuraciones</h3>
                  <p className="mt-1 text-sm">No hay configuraciones que coincidan con los filtros seleccionados.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </ContentGrid>
    </PageLayout>
  );
};

export default MaintenanceConfigView;