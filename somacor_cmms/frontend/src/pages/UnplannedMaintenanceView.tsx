import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  CheckCircle, 
  Send, 
  Plus,
  Clock,
  Wrench,
  FileText,
  Camera,
  User,
  Calendar,
  Search,
  Filter
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import CreateUnplannedMaintenanceForm from '@/components/forms/CreateUnplannedMaintenanceForm';
import UnplannedMaintenanceDetailModal from '@/components/modals/UnplannedMaintenanceDetailModal';
import AssignTechnicianModal from '@/components/modals/AssignTechnicianModal';
import CreateWorkOrderForm from '@/components/forms/CreateWorkOrderForm';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

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

interface MaintenanceStats {
  totalReportes: number;
  pendientes: number;
  enProgreso: number;
  completados: number;
  urgentes: number;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

const UnplannedMaintenanceView: React.FC = () => {
  const [maintenances, setMaintenances] = useState<UnplannedMaintenance[]>([]);
  const [stats, setStats] = useState<MaintenanceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showNewForm, setShowNewForm] = useState(false);
  const [selectedMaintenance, setSelectedMaintenance] = useState<UnplannedMaintenance | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);

  // Datos de ejemplo para el diseño
  const mockMaintenances: UnplannedMaintenance[] = [
    {
      id: '1',
      title: 'Falla en Sistema de Refrigeración',
      equipment: 'Compresor de Aire Principal',
      equipmentCode: 'EQ-001',
      reportedBy: 'Juan Pérez',
      reportedDate: '2024-10-15',
      priority: 'urgente',
      status: 'en_progreso',
      description: 'El compresor presenta sobrecalentamiento y ruidos anormales. La temperatura ha aumentado significativamente.',
      location: 'Planta Norte - Sector A',
      estimatedTime: '4 horas',
      assignedTo: 'María García',
      images: ['image1.jpg', 'image2.jpg']
    },
    {
      id: '2',
      title: 'Fuga de Aceite en Bomba',
      equipment: 'Bomba Centrífuga B-205',
      equipmentCode: 'EQ-002',
      reportedBy: 'Carlos López',
      reportedDate: '2024-10-14',
      priority: 'alta',
      status: 'asignado',
      description: 'Se observa fuga de aceite en la base de la bomba. El nivel de aceite ha bajado considerablemente.',
      location: 'Planta Sur - Sector B',
      estimatedTime: '2 horas',
      assignedTo: 'Pedro Rodríguez'
    },
    {
      id: '3',
      title: 'Vibración Excesiva en Motor',
      equipment: 'Motor Eléctrico C-310',
      equipmentCode: 'EQ-003',
      reportedBy: 'Ana Martínez',
      reportedDate: '2024-10-13',
      priority: 'media',
      status: 'reportado',
      description: 'El motor presenta vibraciones anormales durante el funcionamiento. Se requiere inspección inmediata.',
      location: 'Planta Central - Sector C',
      estimatedTime: '3 horas'
    },
    {
      id: '4',
      title: 'Falla en Válvula de Control',
      equipment: 'Válvula de Control D-115',
      equipmentCode: 'EQ-004',
      reportedBy: 'Luis Fernández',
      reportedDate: '2024-10-12',
      priority: 'baja',
      status: 'completado',
      description: 'La válvula no responde correctamente a las señales de control. Se ha completado la reparación.',
      location: 'Planta Este - Sector D',
      estimatedTime: '1.5 horas',
      assignedTo: 'Roberto Silva'
    }
  ];

  const mockStats: MaintenanceStats = {
    totalReportes: 24,
    pendientes: 8,
    enProgreso: 6,
    completados: 9,
    urgentes: 3
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Importar el servicio de órdenes de trabajo
      const { ordenesTrabajoServiceReal } = await import('@/services/apiServiceReal');
      
      // Cargar todas las órdenes de trabajo
      const response = await ordenesTrabajoServiceReal.getAll({ limit: 100 });
      const ordenes = response.results || response.data || response || [];
      
      // Filtrar órdenes correctivas o de emergencia
      const ordenesNoPlanificadas = ordenes.filter((orden: any) => {
        const tipoMant = orden.tipo_mantenimiento_nombre?.toLowerCase() || '';
        return tipoMant.includes('correctivo') || 
               tipoMant.includes('emergencia') ||
               tipoMant.includes('urgente');
      });
      
      const mantenimientosTransformados = ordenesNoPlanificadas.map((orden: any) => {
        // Determinar prioridad
        let prioridad = orden.prioridad?.toLowerCase() || 'media';
        if (prioridad === 'crítica') prioridad = 'urgente';
        
        // Determinar estado
        let estado = 'reportado';
        const estadoNombre = orden.estado_nombre?.toLowerCase() || '';
        if (estadoNombre.includes('completada') || estadoNombre.includes('cerrada')) {
          estado = 'completado';
        } else if (estadoNombre.includes('progreso')) {
          estado = 'en_progreso';
        } else if (estadoNombre.includes('asignada')) {
          estado = 'asignado';
        }
        
        return {
          id: orden.idordentrabajo?.toString() || orden.id?.toString(),
          title: orden.descripcionproblemareportado || 'Reporte de falla',
          equipment: orden.equipo_nombre || 'Sin equipo',
          equipmentCode: orden.numeroot || 'N/A',
          reportedBy: orden.solicitante_nombre || 'Sin reportar',
          reportedDate: orden.fechareportefalla?.split('T')[0] || new Date().toISOString().split('T')[0],
          priority: prioridad as 'baja' | 'media' | 'alta' | 'urgente',
          status: estado as 'reportado' | 'en_revision' | 'asignado' | 'en_progreso' | 'completado' | 'cancelado',
          description: orden.observacionesfinales || orden.descripcionproblemareportado || '',
          location: orden.faena_nombre || 'Sin ubicación',
          estimatedTime: '2 horas',
          assignedTo: orden.tecnico_nombre,
          images: [],
          // Guardar la orden completa para edición
          _ordenOriginal: orden
        };
      });
      
      setMaintenances(mantenimientosTransformados);
      
      setStats({
        totalReportes: mantenimientosTransformados.length,
        pendientes: mantenimientosTransformados.filter((m: any) => m.status === 'reportado').length,
        enProgreso: mantenimientosTransformados.filter((m: any) => m.status === 'en_progreso').length,
        completados: mantenimientosTransformados.filter((m: any) => m.status === 'completado').length,
        urgentes: mantenimientosTransformados.filter((m: any) => m.priority === 'urgente').length
      });
      
      console.log('✅ Mantenimientos no planificados cargados:', mantenimientosTransformados.length);
    } catch (err: any) {
      console.error("❌ Error fetching maintenance data:", err);
      setError(`Error al cargar mantenimientos: ${err.message || 'Error desconocido'}`);
      setMaintenances([]);
      setStats({ totalReportes: 0, pendientes: 0, enProgreso: 0, completados: 0, urgentes: 0 });
    } finally {
      setLoading(false);
    }
  };

  // Manejar acciones
  const handleView = (maintenance: UnplannedMaintenance) => {
    setSelectedMaintenance(maintenance);
    setShowDetailModal(true);
  };

  const handleEdit = (maintenance: UnplannedMaintenance) => {
    setSelectedMaintenance(maintenance);
    setShowDetailModal(false);
    setShowEditForm(true);
  };

  const handleAssign = (maintenance: UnplannedMaintenance) => {
    setSelectedMaintenance(maintenance);
    setShowDetailModal(false);
    setShowAssignModal(true);
  };

  // Filtrar mantenimientos
  const filteredMaintenances = maintenances.filter(maintenance => {
    const matchesSearch = maintenance.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         maintenance.equipment.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         maintenance.equipmentCode.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesPriority = priorityFilter === 'all' || maintenance.priority === priorityFilter;
    const matchesStatus = statusFilter === 'all' || maintenance.status === statusFilter;
    
    return matchesSearch && matchesPriority && matchesStatus;
  });

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
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'reportado':
        return <Badge variant="default" className="bg-yellow-100 text-yellow-800"><Clock className="h-3 w-3 mr-1" />Reportado</Badge>;
      case 'en_revision':
        return <Badge variant="default" className="bg-blue-100 text-blue-800"><FileText className="h-3 w-3 mr-1" />En Revisión</Badge>;
      case 'asignado':
        return <Badge variant="default" className="bg-purple-100 text-purple-800"><User className="h-3 w-3 mr-1" />Asignado</Badge>;
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
        title="Mantenimiento No Planificado" 
        subtitle="Reporte y gestión de fallas y mantenimientos de emergencia"
      >
        <Button onClick={() => setShowNewForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Reporte
        </Button>
      </PageHeader>

      {/* Tarjetas de estadísticas */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Reportes</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalReportes}</div>
            <p className="text-xs text-muted-foreground">
              Reportes este mes
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pendientes</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats?.pendientes}</div>
            <p className="text-xs text-muted-foreground">
              Requieren asignación
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">En Progreso</CardTitle>
            <Wrench className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.enProgreso}</div>
            <p className="text-xs text-muted-foreground">
              Activamente en reparación
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Urgentes</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{stats?.urgentes}</div>
            <p className="text-xs text-muted-foreground">
              Requieren atención inmediata
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Lista de mantenimientos */}
      <ContentGrid>
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
              <div>
                <CardTitle>Reportes de Mantenimiento</CardTitle>
                <CardDescription>
                  Lista de fallas y mantenimientos no planificados
                </CardDescription>
              </div>
              
              <div className="flex flex-col md:flex-row gap-2 w-full md:w-auto">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar reporte..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-full md:w-64"
                  />
                </div>
                
                <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Prioridad" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas las prioridades</SelectItem>
                    <SelectItem value="baja">Baja</SelectItem>
                    <SelectItem value="media">Media</SelectItem>
                    <SelectItem value="alta">Alta</SelectItem>
                    <SelectItem value="urgente">Urgente</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Estado" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los estados</SelectItem>
                    <SelectItem value="reportado">Reportado</SelectItem>
                    <SelectItem value="en_revision">En Revisión</SelectItem>
                    <SelectItem value="asignado">Asignado</SelectItem>
                    <SelectItem value="en_progreso">En Progreso</SelectItem>
                    <SelectItem value="completado">Completado</SelectItem>
                    <SelectItem value="cancelado">Cancelado</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredMaintenances.map(maintenance => (
                <div key={maintenance.id} className="border rounded-lg p-4 hover:bg-muted/50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-medium">{maintenance.title}</h4>
                        {getPriorityBadge(maintenance.priority)}
                        {getStatusBadge(maintenance.status)}
                      </div>
                      
                      <div className="text-sm text-muted-foreground space-y-1">
                        <div className="flex items-center gap-2">
                          <Wrench className="h-3 w-3" />
                          {maintenance.equipment} ({maintenance.equipmentCode})
                        </div>
                        <div className="flex items-center gap-2">
                          <User className="h-3 w-3" />
                          Reportado por: {maintenance.reportedBy}
                        </div>
                        <div className="flex items-center gap-2">
                          <Calendar className="h-3 w-3" />
                          {maintenance.reportedDate}
                        </div>
                        <div className="flex items-center gap-2">
                          <FileText className="h-3 w-3" />
                          {maintenance.location}
                        </div>
                        {maintenance.assignedTo && (
                          <div className="flex items-center gap-2">
                            <User className="h-3 w-3" />
                            Asignado a: {maintenance.assignedTo}
                          </div>
                        )}
                        {maintenance.estimatedTime && (
                          <div className="flex items-center gap-2">
                            <Clock className="h-3 w-3" />
                            Tiempo estimado: {maintenance.estimatedTime}
                          </div>
                        )}
                        {maintenance.images && maintenance.images.length > 0 && (
                          <div className="flex items-center gap-2">
                            <Camera className="h-3 w-3" />
                            {maintenance.images.length} imagen(es) adjunta(s)
                          </div>
                        )}
                      </div>
                      
                      <p className="text-sm mt-2 text-muted-foreground">
                        {maintenance.description}
                      </p>
                    </div>
                    
                    <div className="flex gap-1 ml-4">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleView(maintenance)}
                        title="Ver detalles"
                      >
                        Ver
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleEdit(maintenance)}
                        title="Editar reporte"
                      >
                        Editar
                      </Button>
                      {maintenance.status === 'reportado' && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleAssign(maintenance)}
                          title="Asignar técnico"
                        >
                          Asignar
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {filteredMaintenances.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <AlertTriangle className="mx-auto h-12 w-12 text-muted-foreground/50" />
                  <h3 className="mt-2 text-sm font-medium">No se encontraron reportes</h3>
                  <p className="mt-1 text-sm">No hay reportes que coincidan con los filtros seleccionados.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </ContentGrid>

      {/* Formulario de creación de mantenimiento no planificado */}
      <CreateUnplannedMaintenanceForm
        isOpen={showNewForm}
        onClose={() => setShowNewForm(false)}
        onSuccess={() => {
          setShowNewForm(false);
          fetchData();
          console.log('Mantenimiento no planificado creado exitosamente');
        }}
      />

      {/* Modal de detalles del mantenimiento */}
      <UnplannedMaintenanceDetailModal
        isOpen={showDetailModal}
        onClose={() => {
          setShowDetailModal(false);
          setSelectedMaintenance(null);
        }}
        maintenance={selectedMaintenance}
        onEdit={handleEdit}
        onAssign={handleAssign}
      />

      {/* Formulario de edición (usando CreateWorkOrderForm) */}
      {selectedMaintenance && (() => {
        const ordenOriginal = (selectedMaintenance as any)._ordenOriginal;
        console.log('🔍 selectedMaintenance:', selectedMaintenance);
        console.log('🔍 _ordenOriginal:', ordenOriginal);
        
        return (
          <CreateWorkOrderForm
            isOpen={showEditForm}
            onClose={() => {
              setShowEditForm(false);
              setSelectedMaintenance(null);
            }}
            onSuccess={() => {
              setShowEditForm(false);
              setSelectedMaintenance(null);
              fetchData();
            }}
            ordenData={ordenOriginal}
          />
        );
      })()}

      {/* Modal de asignación de técnico */}
      {selectedMaintenance && (
        <AssignTechnicianModal
          isOpen={showAssignModal}
          onClose={() => {
            setShowAssignModal(false);
            setSelectedMaintenance(null);
          }}
          maintenanceId={selectedMaintenance.id}
          maintenanceTitle={selectedMaintenance.title}
          onSuccess={() => {
            setShowAssignModal(false);
            setSelectedMaintenance(null);
            fetchData();
          }}
        />
      )}
    </PageLayout>
  );
};

export default UnplannedMaintenanceView;