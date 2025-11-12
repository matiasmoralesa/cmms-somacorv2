import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { 
  ClipboardList, 
  Search, 
  Filter, 
  Plus, 
  Eye, 
  Edit, 
  Trash2,
  AlertTriangle,
  CheckCircle,
  Clock,
  XCircle,
  Wrench,
  Calendar,
  User
} from 'lucide-react';
import CreateWorkOrderForm from '@/components/forms/CreateWorkOrderForm';
import { useRealtimeUpdates } from '@/hooks/useRealtimeUpdates';
import ConnectionStatus from '@/components/ConnectionStatus';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import apiClient from '@/api/apiClient';

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
  idtipomantenimientoot: number;
  tipo_mantenimiento_nombre?: string;
}

interface OrdenesStats {
  pendientes: number;
  enProgreso: number;
  completadas: number;
  urgentes: number;
}

interface Filters {
  statuses: string[];
  types: string[];
  priorities: string[];
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

export default function OrdenesTrabajoView() {
  const navigate = useNavigate();
  const [ordenes, setOrdenes] = useState<OrdenTrabajo[]>([]);
  const [stats, setStats] = useState<OrdenesStats | null>(null);
  const [filters, setFilters] = useState<Filters>({ statuses: [], types: [], priorities: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{isOpen: boolean, orden: OrdenTrabajo | null}>({isOpen: false, orden: null});
  
  // Real-time updates
  const { realtimeData, connectionStatus, subscribeToUpdates } = useRealtimeUpdates({
    onDataUpdate: (dataType, data) => {
      console.log('Ordenes data updated:', dataType, data);
      // Refresh ordenes data when real-time updates are received
      if (dataType === 'ordenes_update') {
        loadInitialData();
        loadOrdenes();
      }
    }
  });
  
  // Filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedPriority, setSelectedPriority] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [sortBy, setSortBy] = useState('fecha_desc'); // Ordenar por última fecha agregada por defecto

  // =================================================================================
  // EFECTOS
  // =================================================================================

  useEffect(() => {
    loadInitialData();
    // Subscribe to ordenes updates
    subscribeToUpdates('ordenes');
  }, []);

  useEffect(() => {
    loadOrdenes();
  }, [searchTerm, selectedStatus, selectedPriority, selectedType, sortBy]);

  // =================================================================================
  // FUNCIONES
  // =================================================================================

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Cargar órdenes para calcular estadísticas
      const response = await apiClient.get('v2/ordenes-trabajo/');
      const ordenesData = response.data.results || response.data || [];

      // Calcular estadísticas localmente
      const statsCalculadas = {
        pendientes: ordenesData.filter((o: OrdenTrabajo) => 
          o.estado_nombre === 'Abierta' || o.estado_nombre === 'Pendiente'
        ).length,
        enProgreso: ordenesData.filter((o: OrdenTrabajo) => 
          o.estado_nombre === 'En Progreso' || o.estado_nombre === 'Asignada'
        ).length,
        completadas: ordenesData.filter((o: OrdenTrabajo) => 
          o.estado_nombre === 'Completada'
        ).length,
        urgentes: ordenesData.filter((o: OrdenTrabajo) => 
          o.prioridad === 'Crítica' || o.prioridad === 'Alta'
        ).length
      };

      setStats(statsCalculadas);
      setError(null); // Limpiar cualquier error previo
    } catch (err) {
      console.error('Error loading initial data:', err);
      // No mostrar error si las órdenes se cargan correctamente después
    } finally {
      setLoading(false);
    }
  };

  const loadOrdenes = async () => {
    try {
      const params: any = {};
      
      if (searchTerm) params.search = searchTerm;
      if (selectedStatus !== 'all') params.status = selectedStatus;
      if (selectedPriority !== 'all') params.priority = selectedPriority;
      if (selectedType !== 'all') params.type = selectedType;

      const response = await apiClient.get('v2/ordenes-trabajo/', { params });
      
      // Asegurar que ordenes sea siempre un array
      let ordenesData = [];
      if (response.data && Array.isArray(response.data.results)) {
        ordenesData = response.data.results;
      } else if (Array.isArray(response.data)) {
        ordenesData = response.data;
      } else {
        console.warn('Respuesta inesperada del servicio de órdenes:', response.data);
        ordenesData = [];
      }
      
      // Usar directamente los datos del backend
      setOrdenes(ordenesData);
    } catch (err) {
      console.error('Error loading ordenes:', err);
      setError('Error al cargar las órdenes de trabajo');
      setOrdenes([]); // Asegurar que ordenes sea un array vacío en caso de error
    }
  };

  const getPriorityColor = (priority: string) => {
    if (!priority || typeof priority !== 'string') {
      return 'default';
    }
    
    switch (priority.toLowerCase()) {
      case 'crítica':
      case 'urgente':
        return 'destructive';
      case 'alta':
        return 'destructive';
      case 'media':
        return 'default';
      case 'baja':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    if (!status || typeof status !== 'string') {
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100';
    }
    
    switch (status.toLowerCase()) {
      case 'completada':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100';
      case 'en progreso':
      case 'en proceso':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100';
      case 'pendiente':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100';
      case 'abierta':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100';
      case 'asignada':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100';
      case 'cancelada':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100';
    }
  };

  const getPriorityIcon = (priority: string) => {
    if (!priority || typeof priority !== 'string') {
      return <Clock className="h-4 w-4" />;
    }
    
    switch (priority.toLowerCase()) {
      case 'crítica':
      case 'urgente':
        return <AlertTriangle className="h-4 w-4" />;
      case 'alta':
        return <AlertTriangle className="h-4 w-4" />;
      case 'media':
        return <Clock className="h-4 w-4" />;
      case 'baja':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getTypeIcon = (type: string) => {
    if (!type || typeof type !== 'string') {
      return <ClipboardList className="h-4 w-4" />;
    }
    
    switch (type.toLowerCase()) {
      case 'preventivo':
        return <Calendar className="h-4 w-4" />;
      case 'correctivo':
        return <Wrench className="h-4 w-4" />;
      case 'modificativo':
        return <Wrench className="h-4 w-4" />;
      case 'emergencia':
        return <AlertTriangle className="h-4 w-4" />;
      case 'predictivo':
        return <Clock className="h-4 w-4" />;
      default:
        return <ClipboardList className="h-4 w-4" />;
    }
  };

  const handleViewDetails = (orden: OrdenTrabajo) => {
    console.log('Ver detalles de:', orden);
    navigate(`/ordenes-trabajo/${orden.idordentrabajo}`);
  };

  const handleEdit = (orden: OrdenTrabajo) => {
    console.log('Editar orden:', orden);
    navigate(`/ordenes-trabajo/${orden.idordentrabajo}`);
  };

  const handleDelete = (orden: OrdenTrabajo) => {
    setDeleteConfirm({isOpen: true, orden});
  };

  const confirmDelete = async () => {
    if (!deleteConfirm.orden) return;
    
    try {
      await apiClient.delete(`v2/ordenes-trabajo/${deleteConfirm.orden.idordentrabajo}/`);
      
      // Actualizar lista localmente sin recargar
      const ordenesActualizadas = ordenes.filter(o => o.idordentrabajo !== deleteConfirm.orden!.idordentrabajo);
      setOrdenes(ordenesActualizadas);
      
      // Actualizar estadísticas localmente
      if (stats) {
        const ordenEliminada = deleteConfirm.orden;
        const nuevasStats = { ...stats };
        
        if (ordenEliminada.estado_nombre === 'Abierta' || ordenEliminada.estado_nombre === 'Pendiente') {
          nuevasStats.pendientes = Math.max(0, nuevasStats.pendientes - 1);
        } else if (ordenEliminada.estado_nombre === 'En Progreso' || ordenEliminada.estado_nombre === 'Asignada') {
          nuevasStats.enProgreso = Math.max(0, nuevasStats.enProgreso - 1);
        } else if (ordenEliminada.estado_nombre === 'Completada') {
          nuevasStats.completadas = Math.max(0, nuevasStats.completadas - 1);
        }
        
        if (ordenEliminada.prioridad === 'Crítica' || ordenEliminada.prioridad === 'Alta') {
          nuevasStats.urgentes = Math.max(0, nuevasStats.urgentes - 1);
        }
        
        setStats(nuevasStats);
      }
      
      // Cerrar modal y limpiar error
      setDeleteConfirm({isOpen: false, orden: null});
      setError(null);
    } catch (err: any) {
      console.error('Error eliminando orden:', err);
      setError(`Error al eliminar la orden: ${err.response?.data?.detail || err.message}`);
      setDeleteConfirm({isOpen: false, orden: null});
    }
  };

  const cancelDelete = () => {
    setDeleteConfirm({isOpen: false, orden: null});
  };

  // =================================================================================
  // RENDER
  // =================================================================================

  if (loading && !ordenes.length) {
    return (
      <PageLayout>
        <PageHeader
          title="Órdenes de Trabajo"
          description="Cargando órdenes de trabajo..."
        />
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Cargando órdenes de trabajo...</p>
          </div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader
        title="Órdenes de Trabajo"
        description="Gestión de órdenes de trabajo y mantenimiento"
        action={
          <div className="flex items-center gap-3">
            <ConnectionStatus status={connectionStatus} />
            <Button 
              className="bg-primary hover:bg-primary/90"
              onClick={() => setShowCreateForm(true)}
            >
              <Plus className="h-4 w-4 mr-2" />
              Nueva Orden
            </Button>
          </div>
        }
      />

      {/* Estadísticas */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pendientes</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats?.pendientes || 0}</div>
            <p className="text-xs text-muted-foreground">
              Esperando asignación
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">En Progreso</CardTitle>
            <Wrench className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.enProgreso || 0}</div>
            <p className="text-xs text-muted-foreground">
              En ejecución
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completadas</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.completadas || 0}</div>
            <p className="text-xs text-muted-foreground">
              Finalizadas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Urgentes</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats?.urgentes || 0}</div>
            <p className="text-xs text-muted-foreground">
              Requieren atención inmediata
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Filtros y búsqueda */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros y Búsqueda</CardTitle>
          <CardDescription>Buscar y filtrar órdenes de trabajo por diferentes criterios</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por descripción, equipo o técnico..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los estados</SelectItem>
                <SelectItem value="Abierta">Abierta</SelectItem>
                <SelectItem value="Asignada">Asignada</SelectItem>
                <SelectItem value="En Progreso">En Progreso</SelectItem>
                <SelectItem value="Completada">Completada</SelectItem>
                <SelectItem value="Cancelada">Cancelada</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Ordenar por" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="fecha_desc">Más recientes primero</SelectItem>
                <SelectItem value="fecha_asc">Más antiguas primero</SelectItem>
                <SelectItem value="prioridad">Por prioridad</SelectItem>
                <SelectItem value="numero">Por número de OT</SelectItem>
              </SelectContent>
            </Select>

            <Select value={selectedPriority} onValueChange={setSelectedPriority}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Prioridad" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas las prioridades</SelectItem>
                <SelectItem value="Crítica">Crítica</SelectItem>
                <SelectItem value="Alta">Alta</SelectItem>
                <SelectItem value="Media">Media</SelectItem>
                <SelectItem value="Baja">Baja</SelectItem>
              </SelectContent>
            </Select>

            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Tipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los tipos</SelectItem>
                <SelectItem value="Preventivo">Preventivo</SelectItem>
                <SelectItem value="Correctivo">Correctivo</SelectItem>
                <SelectItem value="Predictivo">Predictivo</SelectItem>
                <SelectItem value="Emergencia">Emergencia</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabla de órdenes de trabajo */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Órdenes de Trabajo</CardTitle>
          <CardDescription>
            {ordenes.length} órdenes encontradas
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">{error}</p>
            </div>
          )}
          
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Descripción</TableHead>
                  <TableHead>Equipo</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Prioridad</TableHead>
                  <TableHead>Asignado a</TableHead>
                  <TableHead>Fecha Programada</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {ordenes.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                      No se encontraron órdenes de trabajo
                    </TableCell>
                  </TableRow>
                ) : (
                  ordenes.map((orden) => (
                    <TableRow key={orden.idordentrabajo}>
                      <TableCell className="font-medium">{orden.numeroot}</TableCell>
                      <TableCell>{orden.descripcionproblemareportado}</TableCell>
                      <TableCell>{orden.equipo_nombre}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getTypeIcon(orden.tipo_mantenimiento_nombre || '')}
                          {orden.tipo_mantenimiento_nombre || 'N/A'}
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(orden.estado_nombre)}`}>
                          {orden.estado_nombre}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getPriorityColor(orden.prioridad)} className="flex items-center gap-1 w-fit">
                          {getPriorityIcon(orden.prioridad)}
                          {orden.prioridad}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4 text-muted-foreground" />
                          {orden.tecnico_nombre || 'Sin asignar'}
                        </div>
                      </TableCell>
                      <TableCell>{new Date(orden.fechareportefalla).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewDetails(orden)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(orden)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(orden)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Formulario de creación de orden de trabajo */}
      <CreateWorkOrderForm
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={() => {
          loadInitialData(); // Recargar datos después de crear
          loadOrdenes(); // Recargar lista de órdenes
        }}
      />

      {/* Diálogo de confirmación de eliminación */}
      <AlertDialog open={deleteConfirm.isOpen} onOpenChange={(open) => !open && cancelDelete()}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Eliminar orden de trabajo?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará permanentemente la orden de trabajo{' '}
              <strong>{deleteConfirm.orden?.numeroot}</strong>.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={cancelDelete}>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Eliminar
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </PageLayout>
  );
}