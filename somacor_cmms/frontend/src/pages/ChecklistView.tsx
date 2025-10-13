import React, { useState, useEffect } from 'react';
import { 
  ClipboardCheck, 
  Plus, 
  Search, 
  Filter,
  CheckCircle,
  XCircle,
  Clock,
  User,
  Calendar,
  Wrench,
  FileText,
  Camera,
  Send,
  Save,
  Edit,
  Trash2,
  Eye,
  AlertTriangle
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import CreateChecklistForm from '@/components/forms/CreateChecklistForm';
import { checklistService } from '@/services/checklistService';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface Checklist {
  id: number;
  name: string;
  equipment: string;
  equipmentCode: string;
  technician: string;
  date: string;
  status: 'pendiente' | 'en_progreso' | 'completado' | 'cancelado';
  totalItems: number;
  completedItems: number;
  failedItems: number;
  observations?: string;
  images?: string[];
  createdAt: string;
  completedAt?: string;
}

interface ChecklistStats {
  totalChecklists: number;
  pendingChecklists: number;
  inProgressChecklists: number;
  completedChecklists: number;
  averageCompletion: number;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

const ChecklistView: React.FC = () => {
  const [checklists, setChecklists] = useState<Checklist[]>([]);
  const [stats, setStats] = useState<ChecklistStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [equipmentFilter, setEquipmentFilter] = useState('all');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedChecklist, setSelectedChecklist] = useState<Checklist | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  // Datos de ejemplo para el diseño
  const mockChecklists: Checklist[] = [
    {
      id: 1,
      name: 'Checklist Diario Compresor A-101',
      equipment: 'Compresor de Aire Principal',
      equipmentCode: 'EQ-001',
      technician: 'Juan Pérez',
      date: '2024-10-15',
      status: 'completado',
      totalItems: 15,
      completedItems: 14,
      failedItems: 1,
      observations: 'Equipo en buen estado general, se detectó fuga menor en válvula de drenaje',
      images: ['checklist_1.jpg', 'valve_leak.jpg'],
      createdAt: '2024-10-15',
      completedAt: '2024-10-15'
    },
    {
      id: 2,
      name: 'Checklist Semanal Bomba B-205',
      equipment: 'Bomba Centrífuga B-205',
      equipmentCode: 'EQ-002',
      technician: 'María García',
      date: '2024-10-16',
      status: 'en_progreso',
      totalItems: 12,
      completedItems: 8,
      failedItems: 0,
      createdAt: '2024-10-16'
    },
    {
      id: 3,
      name: 'Checklist Mensual Motor C-310',
      equipment: 'Motor Eléctrico C-310',
      equipmentCode: 'EQ-003',
      technician: 'Carlos López',
      date: '2024-10-17',
      status: 'pendiente',
      totalItems: 20,
      completedItems: 0,
      failedItems: 0,
      createdAt: '2024-10-17'
    },
    {
      id: 4,
      name: 'Checklist Trimestral Válvula D-115',
      equipment: 'Válvula de Control D-115',
      equipmentCode: 'EQ-004',
      technician: 'Ana Martínez',
      date: '2024-10-18',
      status: 'cancelado',
      totalItems: 8,
      completedItems: 3,
      failedItems: 0,
      observations: 'Cancelado por falta de repuestos necesarios',
      createdAt: '2024-10-18'
    }
  ];

  const mockStats: ChecklistStats = {
    totalChecklists: 24,
    pendingChecklists: 8,
    inProgressChecklists: 5,
    completedChecklists: 11,
    averageCompletion: 85
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // TODO: Cargar datos reales del backend
      // const data = await checklistService.getInstances();
      // setChecklists(data.results);
      
      // Usar datos mock por ahora
      setChecklists(mockChecklists);
      setStats(mockStats);
    } catch (err) {
      console.error("Error fetching checklists data:", err);
      setError("No se pudo cargar la información de checklists.");
    } finally {
      setLoading(false);
    }
  };

  // Filtrar checklists
  const filteredChecklists = checklists.filter(checklist => {
    const matchesSearch = checklist.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         checklist.equipment.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         checklist.equipmentCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         checklist.technician.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || checklist.status === statusFilter;
    const matchesEquipment = equipmentFilter === 'all' || checklist.equipmentCode === equipmentFilter;
    
    return matchesSearch && matchesStatus && matchesEquipment;
  });

  // Handlers para acciones
  const handleViewDetails = (checklist: Checklist) => {
    setSelectedChecklist(checklist);
    console.log('Ver detalles de:', checklist.name);
  };

  const handleEdit = (checklist: Checklist) => {
    setSelectedChecklist(checklist);
    console.log('Editar checklist:', checklist.name);
  };

  const handleDelete = (checklist: Checklist) => {
    setSelectedChecklist(checklist);
    setShowDeleteDialog(true);
  };

  const confirmDelete = () => {
    if (selectedChecklist) {
      console.log('Eliminar checklist:', selectedChecklist.name);
      setShowDeleteDialog(false);
      setSelectedChecklist(null);
    }
  };

  // Obtener badge de estado
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pendiente':
        return <Badge variant="secondary"><Clock className="h-3 w-3 mr-1" />Pendiente</Badge>;
      case 'en_progreso':
        return <Badge variant="default" className="bg-blue-100 text-blue-800"><ClipboardCheck className="h-3 w-3 mr-1" />En Progreso</Badge>;
      case 'completado':
        return <Badge variant="default" className="bg-green-100 text-green-800"><CheckCircle className="h-3 w-3 mr-1" />Completado</Badge>;
      case 'cancelado':
        return <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" />Cancelado</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  // Calcular porcentaje de completado
  const getCompletionPercentage = (completed: number, total: number) => {
    return total > 0 ? Math.round((completed / total) * 100) : 0;
  };

  // Obtener badge de progreso
  const getProgressBadge = (completed: number, total: number) => {
    const percentage = getCompletionPercentage(completed, total);
    if (percentage === 100) {
      return <Badge variant="default" className="bg-green-100 text-green-800">{percentage}%</Badge>;
    } else if (percentage >= 75) {
      return <Badge variant="default" className="bg-blue-100 text-blue-800">{percentage}%</Badge>;
    } else if (percentage >= 50) {
      return <Badge variant="default" className="bg-yellow-100 text-yellow-800">{percentage}%</Badge>;
    } else {
      return <Badge variant="default" className="bg-red-100 text-red-800">{percentage}%</Badge>;
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
        title="Checklists de Mantenimiento" 
        subtitle="Gestión y seguimiento de listas de verificación"
      >
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Checklist
        </Button>
      </PageHeader>

      {/* Tarjetas de estadísticas */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Checklists</CardTitle>
            <ClipboardCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalChecklists}</div>
            <p className="text-xs text-muted-foreground">
              Checklists registrados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pendientes</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats?.pendingChecklists}</div>
            <p className="text-xs text-muted-foreground">
              Requieren ejecución
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">En Progreso</CardTitle>
            <ClipboardCheck className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.inProgressChecklists}</div>
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
            <div className="text-2xl font-bold text-green-600">{stats?.completedChecklists}</div>
            <p className="text-xs text-muted-foreground">
              {stats ? Math.round((stats.completedChecklists / stats.totalChecklists) * 100) : 0}% del total
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Lista de checklists */}
      <ContentGrid>
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
              <div>
                <CardTitle>Lista de Checklists</CardTitle>
                <CardDescription>
                  Listas de verificación y seguimiento de mantenimiento
                </CardDescription>
              </div>
              
              <div className="flex flex-col md:flex-row gap-2 w-full md:w-auto">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar checklist..."
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
                    <SelectItem value="pendiente">Pendiente</SelectItem>
                    <SelectItem value="en_progreso">En Progreso</SelectItem>
                    <SelectItem value="completado">Completado</SelectItem>
                    <SelectItem value="cancelado">Cancelado</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={equipmentFilter} onValueChange={setEquipmentFilter}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Equipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los equipos</SelectItem>
                    <SelectItem value="EQ-001">EQ-001</SelectItem>
                    <SelectItem value="EQ-002">EQ-002</SelectItem>
                    <SelectItem value="EQ-003">EQ-003</SelectItem>
                    <SelectItem value="EQ-004">EQ-004</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredChecklists.map(checklist => (
                <div key={checklist.id} className="border rounded-lg p-4 hover:bg-muted/50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-medium">{checklist.name}</h4>
                        {getStatusBadge(checklist.status)}
                        {getProgressBadge(checklist.completedItems, checklist.totalItems)}
                      </div>
                      
                      <div className="text-sm text-muted-foreground space-y-1">
                        <div className="flex items-center gap-2">
                          <Wrench className="h-3 w-3" />
                          {checklist.equipment} ({checklist.equipmentCode})
                        </div>
                        <div className="flex items-center gap-2">
                          <User className="h-3 w-3" />
                          Técnico: {checklist.technician}
                        </div>
                        <div className="flex items-center gap-2">
                          <Calendar className="h-3 w-3" />
                          Fecha: {checklist.date}
                        </div>
                        <div className="flex items-center gap-2">
                          <FileText className="h-3 w-3" />
                          Items: {checklist.completedItems}/{checklist.totalItems} completados
                          {checklist.failedItems > 0 && (
                            <span className="text-red-600">({checklist.failedItems} fallos)</span>
                          )}
                        </div>
                        {checklist.images && checklist.images.length > 0 && (
                          <div className="flex items-center gap-2">
                            <Camera className="h-3 w-3" />
                            {checklist.images.length} imagen(es) adjunta(s)
                          </div>
                        )}
                      </div>
                      
                      {checklist.observations && (
                        <div className="mt-3 p-2 bg-muted/50 rounded text-sm">
                          <strong>Observaciones:</strong> {checklist.observations}
                        </div>
                      )}
                      
                      {/* Barra de progreso */}
                      <div className="mt-3">
                        <div className="flex justify-between text-xs text-muted-foreground mb-1">
                          <span>Progreso</span>
                          <span>{getCompletionPercentage(checklist.completedItems, checklist.totalItems)}%</span>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2">
                          <div 
                            className="bg-primary h-2 rounded-full transition-all duration-300"
                            style={{ width: `${getCompletionPercentage(checklist.completedItems, checklist.totalItems)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-1 ml-4">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleViewDetails(checklist)}
                        title="Ver detalles"
                      >
                        <Eye className="h-3 w-3" />
                      </Button>
                      {checklist.status === 'pendiente' && (
                        <Button variant="outline" size="sm" title="Iniciar">
                          <ClipboardCheck className="h-3 w-3" />
                        </Button>
                      )}
                      {checklist.status === 'en_progreso' && (
                        <Button variant="outline" size="sm" title="Guardar">
                          <Save className="h-3 w-3" />
                        </Button>
                      )}
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleEdit(checklist)}
                        title="Editar"
                      >
                        <Edit className="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDelete(checklist)}
                        title="Eliminar"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              
              {filteredChecklists.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <ClipboardCheck className="mx-auto h-12 w-12 text-muted-foreground/50" />
                  <h3 className="mt-2 text-sm font-medium">No se encontraron checklists</h3>
                  <p className="mt-1 text-sm">No hay checklists que coincidan con los filtros seleccionados.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </ContentGrid>

      {/* Formulario de creación de checklist */}
      <CreateChecklistForm
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={() => {
          fetchData();
        }}
      />

      {/* Diálogo de confirmación de eliminación */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Estás seguro?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará permanentemente el checklist "{selectedChecklist?.name}".
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Eliminar
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </PageLayout>
  );
};

export default ChecklistView;