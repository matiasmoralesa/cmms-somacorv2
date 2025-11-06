import React, { useState, useEffect } from 'react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { 
  Wrench, 
  Search, 
  Filter, 
  Plus, 
  Eye, 
  Edit, 
  Trash2,
  AlertTriangle,
  CheckCircle,
  Clock,
  XCircle
} from 'lucide-react';
import { equiposService } from '@/services/apiService';
import CreateEquipmentForm from '@/components/forms/CreateEquipmentForm';
import { useRealtimeUpdates } from '@/hooks/useRealtimeUpdates';
import ConnectionStatus from '@/components/ConnectionStatus';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface Equipo {
  id: number;
  codigo: string;
  nombre: string;
  marca: string;
  modelo: string;
  patente: string;
  ubicacion: string;
  estado: string;
  categoria: string;
  ultimoMantenimiento: string;
  activo: boolean;
}

interface EquiposStats {
  total: number;
  operativos: number;
  enMantenimiento: number;
  fueraServicio: number;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

export default function EquiposMovilesView() {
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [stats, setStats] = useState<EquiposStats | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [states, setStates] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  
  // Real-time updates
  const { realtimeData, connectionStatus, subscribeToUpdates } = useRealtimeUpdates({
    onDataUpdate: (dataType, data) => {
      console.log('Equipos data updated:', dataType, data);
      // Refresh equipos data when real-time updates are received
      if (dataType === 'equipos_update') {
        loadInitialData();
        loadEquipos();
      }
    }
  });
  
  // Filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedState, setSelectedState] = useState('all');

  // =================================================================================
  // EFECTOS
  // =================================================================================

  useEffect(() => {
    loadInitialData();
    // Subscribe to equipos updates
    subscribeToUpdates('equipos');
  }, []);

  useEffect(() => {
    loadEquipos();
  }, [searchTerm, selectedCategory, selectedState]);

  // =================================================================================
  // FUNCIONES
  // =================================================================================

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsData, categoriesData, statesData] = await Promise.all([
        equiposService.getStats(),
        equiposService.getCategories(),
        equiposService.getStates()
      ]);

      // Transformar las estadísticas al formato esperado
      const statsTransformados = {
        total: statsData.total_equipos || statsData.total || 0,
        operativos: statsData.equipos_activos || statsData.operativos || 0,
        enMantenimiento: statsData.equipos_en_mantenimiento || statsData.enMantenimiento || 0,
        fueraServicio: statsData.equipos_inactivos || statsData.fueraServicio || 0
      };

      setStats(statsTransformados);
      setCategories(categoriesData || []);
      setStates(statesData || []);
    } catch (err) {
      console.error('Error loading initial data:', err);
      setError('Error al cargar los datos iniciales');
    } finally {
      setLoading(false);
    }
  };

  const loadEquipos = async () => {
    try {
      const params: any = {};
      
      if (searchTerm) params.search = searchTerm;
      if (selectedCategory !== 'all') params.category = selectedCategory;
      if (selectedState !== 'all') params.state = selectedState;

      const response = await equiposService.getList(params);
      
      // Asegurar que equipos sea siempre un array
      let equiposData = [];
      if (response && Array.isArray(response.results)) {
        equiposData = response.results;
      } else if (Array.isArray(response)) {
        equiposData = response;
      } else {
        console.warn('Respuesta inesperada del servicio de equipos:', response);
        equiposData = [];
      }
      
      // Transformar los datos del servicio al formato esperado por el componente
      const equiposTransformados = equiposData.map((equipo: any) => ({
        id: equipo.idequipo || equipo.id,
        codigo: equipo.codigointerno || equipo.codigo,
        nombre: equipo.nombreequipo || equipo.nombre,
        marca: equipo.marca || '',
        modelo: equipo.modelo || '',
        patente: equipo.patente || '',
        ubicacion: equipo.faena_nombre || equipo.ubicacion || 'Sin ubicación',
        estado: equipo.estado_nombre || equipo.estado || 'Sin estado',
        categoria: equipo.tipo_equipo_nombre || equipo.categoria || 'Sin categoría',
        ultimoMantenimiento: equipo.ultima_mantenimiento ? 
          new Date(equipo.ultima_mantenimiento).toLocaleDateString() : 
          'Nunca',
        activo: equipo.activo !== undefined ? equipo.activo : true
      }));
      
      setEquipos(equiposTransformados);
    } catch (err) {
      console.error('Error loading equipos:', err);
      setError('Error al cargar los equipos');
      setEquipos([]); // Asegurar que equipos sea un array vacío en caso de error
    }
  };

  const getEstadoColor = (estado: string) => {
    switch (estado.toLowerCase()) {
      case 'operativo':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100';
      case 'en mantenimiento':
      case 'en mantencion':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100';
      case 'fuera de servicio':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100';
      case 'en reparacion':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100';
      case 'disponible':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100';
    }
  };

  const getEstadoIcon = (estado: string) => {
    switch (estado.toLowerCase()) {
      case 'operativo':
        return <CheckCircle className="h-4 w-4" />;
      case 'en mantenimiento':
      case 'en mantencion':
        return <Clock className="h-4 w-4" />;
      case 'fuera de servicio':
        return <XCircle className="h-4 w-4" />;
      case 'en reparacion':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const handleViewDetails = (equipo: Equipo) => {
    console.log('Ver detalles de:', equipo);
    // TODO: Implementar navegación a detalles del equipo
  };

  const handleEdit = (equipo: Equipo) => {
    console.log('Editar equipo:', equipo);
    // TODO: Implementar edición del equipo
  };

  const handleDelete = (equipo: Equipo) => {
    console.log('Eliminar equipo:', equipo);
    // TODO: Implementar eliminación del equipo
  };

  // =================================================================================
  // RENDER
  // =================================================================================

  if (loading && !equipos.length) {
    return (
      <PageLayout>
        <PageHeader
          title="Equipos Móviles"
          description="Cargando equipos..."
        />
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Cargando equipos...</p>
          </div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader
        title="Equipos Móviles"
        description="Gestión de equipos móviles y su estado operacional"
        action={
          <div className="flex items-center gap-3">
            <ConnectionStatus status={connectionStatus} />
            <Button 
              className="bg-primary hover:bg-primary/90"
              onClick={() => setShowCreateForm(true)}
            >
              <Plus className="h-4 w-4 mr-2" />
              Nuevo Equipo
            </Button>
          </div>
        }
      />

      {/* Estadísticas */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Equipos</CardTitle>
            <Wrench className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total || 0}</div>
            <p className="text-xs text-muted-foreground">
              Equipos registrados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Operativos</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.operativos || 0}</div>
            <p className="text-xs text-muted-foreground">
              En funcionamiento
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">En Mantenimiento</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats?.enMantenimiento || 0}</div>
            <p className="text-xs text-muted-foreground">
              Requieren atención
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Fuera de Servicio</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats?.fueraServicio || 0}</div>
            <p className="text-xs text-muted-foreground">
              No operativos
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Filtros y búsqueda */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros y Búsqueda</CardTitle>
          <CardDescription>Buscar y filtrar equipos por diferentes criterios</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por nombre, código o patente..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Categoría" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas las categorías</SelectItem>
                {categories.map((category) => (
                  <SelectItem key={category} value={category}>
                    {category}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={selectedState} onValueChange={setSelectedState}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los estados</SelectItem>
                {states.map((state) => (
                  <SelectItem key={state} value={state}>
                    {state}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabla de equipos */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Equipos</CardTitle>
          <CardDescription>
            {equipos.length} equipos encontrados
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
                  <TableHead>Código</TableHead>
                  <TableHead>Nombre</TableHead>
                  <TableHead>Marca/Modelo</TableHead>
                  <TableHead>Patente</TableHead>
                  <TableHead>Ubicación</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Categoría</TableHead>
                  <TableHead>Último Mant.</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {equipos.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                      No se encontraron equipos
                    </TableCell>
                  </TableRow>
                ) : (
                  equipos.map((equipo) => (
                    <TableRow key={equipo.id}>
                      <TableCell className="font-medium">{equipo.codigo}</TableCell>
                      <TableCell>{equipo.nombre}</TableCell>
                      <TableCell>
                        {equipo.marca} {equipo.modelo}
                      </TableCell>
                      <TableCell>{equipo.patente}</TableCell>
                      <TableCell>{equipo.ubicacion}</TableCell>
                      <TableCell>
                        <Badge className={`${getEstadoColor(equipo.estado)} flex items-center gap-1 w-fit`}>
                          {getEstadoIcon(equipo.estado)}
                          {equipo.estado}
                        </Badge>
                      </TableCell>
                      <TableCell>{equipo.categoria}</TableCell>
                      <TableCell>{equipo.ultimoMantenimiento}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewDetails(equipo)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(equipo)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(equipo)}
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

      {/* Formulario de creación de equipo */}
      <CreateEquipmentForm
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={() => {
          loadInitialData(); // Recargar datos después de crear
          loadEquipos(); // Recargar lista de equipos
        }}
      />
    </PageLayout>
  );
}