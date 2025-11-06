import React, { useState, useEffect } from 'react';
import { 
  Wrench, 
  Plus, 
  Search, 
  Filter,
  Settings,
  Edit,
  Trash2,
  Eye,
  Package,
  Clock,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import CreateTipoEquipoForm from '@/components/forms/CreateTipoEquipoForm';
import { tiposEquipoService } from '@/services/tiposEquipoService';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface TipoEquipo {
  id: number;
  name: string;
  description: string;
  equipmentCount: number;
  maintenanceFrequency: string;
  isActive: boolean;
  createdAt: string;
  lastUpdated: string;
}

interface TipoEquipoStats {
  totalTipos: number;
  activeTipos: number;
  totalEquipment: number;
  mostCommonType: string;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

const TiposEquipoView: React.FC = () => {
  const [tiposEquipo, setTiposEquipo] = useState<TipoEquipo[]>([]);
  const [stats, setStats] = useState<TipoEquipoStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedTipo, setSelectedTipo] = useState<TipoEquipo | null>(null);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  // Datos de ejemplo para el diseño
  const mockTiposEquipo: TipoEquipo[] = [
    {
      id: 1,
      name: 'Compresores',
      description: 'Equipos de compresión de aire y gases para procesos industriales',
      equipmentCount: 25,
      maintenanceFrequency: 'Mensual',
      isActive: true,
      createdAt: '2024-01-15',
      lastUpdated: '2024-10-15'
    },
    {
      id: 2,
      name: 'Bombas',
      description: 'Bombas centrífugas y de desplazamiento positivo para fluidos',
      equipmentCount: 18,
      maintenanceFrequency: 'Bimensual',
      isActive: true,
      createdAt: '2024-02-20',
      lastUpdated: '2024-10-14'
    },
    {
      id: 3,
      name: 'Motores',
      description: 'Motores eléctricos de diferentes potencias y aplicaciones',
      equipmentCount: 32,
      maintenanceFrequency: 'Trimestral',
      isActive: true,
      createdAt: '2024-03-10',
      lastUpdated: '2024-10-13'
    },
    {
      id: 4,
      name: 'Válvulas',
      description: 'Válvulas de control, seguridad y regulación de flujo',
      equipmentCount: 45,
      maintenanceFrequency: 'Semestral',
      isActive: true,
      createdAt: '2024-04-15',
      lastUpdated: '2024-10-12'
    },
    {
      id: 5,
      name: 'Generadores',
      description: 'Generadores de energía eléctrica de emergencia',
      equipmentCount: 8,
      maintenanceFrequency: 'Mensual',
      isActive: false,
      createdAt: '2024-05-20',
      lastUpdated: '2024-09-20'
    }
  ];

  const mockStats: TipoEquipoStats = {
    totalTipos: 12,
    activeTipos: 10,
    totalEquipment: 156,
    mostCommonType: 'Válvulas'
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // TODO: Cargar datos reales del backend
      // const data = await tiposEquipoService.getAll();
      // setTiposEquipo(data.results);
      
      // Usar datos mock por ahora
      setTiposEquipo(mockTiposEquipo);
      setStats(mockStats);
    } catch (err) {
      console.error("Error fetching equipment types data:", err);
      setError("No se pudo cargar la información de tipos de equipo.");
    } finally {
      setLoading(false);
    }
  };

  // Filtrar tipos de equipo
  const filteredTiposEquipo = tiposEquipo.filter(tipo => {
    return tipo.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           tipo.description.toLowerCase().includes(searchTerm.toLowerCase());
  });

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

  // Obtener badge de frecuencia de mantenimiento
  const getFrequencyBadge = (frequency: string) => {
    switch (frequency) {
      case 'Mensual':
        return <Badge variant="default" className="bg-red-100 text-red-800">Mensual</Badge>;
      case 'Bimensual':
        return <Badge variant="default" className="bg-orange-100 text-orange-800">Bimensual</Badge>;
      case 'Trimestral':
        return <Badge variant="default" className="bg-yellow-100 text-yellow-800">Trimestral</Badge>;
      case 'Semestral':
        return <Badge variant="default" className="bg-green-100 text-green-800">Semestral</Badge>;
      default:
        return <Badge variant="secondary">{frequency}</Badge>;
    }
  };

  // Handlers para acciones
  const handleViewDetails = (tipo: TipoEquipo) => {
    setSelectedTipo(tipo);
    console.log('Ver detalles de:', tipo.name);
  };

  const handleEdit = (tipo: TipoEquipo) => {
    setSelectedTipo(tipo);
    setShowEditForm(true);
  };

  const handleDelete = (tipo: TipoEquipo) => {
    setSelectedTipo(tipo);
    setShowDeleteDialog(true);
  };

  const confirmDelete = () => {
    if (selectedTipo) {
      console.log('Eliminar tipo de equipo:', selectedTipo.name);
      setShowDeleteDialog(false);
      setSelectedTipo(null);
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
        title="Tipos de Equipo" 
        subtitle="Configuración y gestión de categorías de equipos industriales"
      >
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Tipo
        </Button>
      </PageHeader>

      {/* Tarjetas de estadísticas */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tipos</CardTitle>
            <Wrench className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalTipos}</div>
            <p className="text-xs text-muted-foreground">
              Categorías registradas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tipos Activos</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.activeTipos}</div>
            <p className="text-xs text-muted-foreground">
              {stats ? Math.round((stats.activeTipos / stats.totalTipos) * 100) : 0}% del total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Equipos</CardTitle>
            <Package className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.totalEquipment}</div>
            <p className="text-xs text-muted-foreground">
              Equipos categorizados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tipo Más Común</CardTitle>
            <Settings className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{stats?.mostCommonType}</div>
            <p className="text-xs text-muted-foreground">
              Categoría principal
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Lista de tipos de equipo */}
      <ContentGrid>
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
              <div>
                <CardTitle>Lista de Tipos de Equipo</CardTitle>
                <CardDescription>
                  Categorías y configuraciones de equipos industriales
                </CardDescription>
              </div>
              
              <div className="flex flex-col md:flex-row gap-2 w-full md:w-auto">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar tipo de equipo..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-full md:w-64"
                  />
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredTiposEquipo.map(tipo => (
                <div key={tipo.id} className="border rounded-lg p-4 hover:bg-muted/50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-medium">{tipo.name}</h4>
                        {getStatusBadge(tipo.isActive)}
                        {getFrequencyBadge(tipo.maintenanceFrequency)}
                      </div>
                      
                      <p className="text-sm text-muted-foreground mb-3">
                        {tipo.description}
                      </p>
                      
                      <div className="flex gap-4 text-sm">
                        <div className="flex items-center gap-1">
                          <Package className="h-3 w-3 text-blue-600" />
                          <span className="text-blue-600 font-medium">{tipo.equipmentCount}</span>
                          <span className="text-muted-foreground">equipos</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3 text-green-600" />
                          <span className="text-green-600 font-medium">Frecuencia:</span>
                          <span className="text-muted-foreground">{tipo.maintenanceFrequency}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Settings className="h-3 w-3 text-purple-600" />
                          <span className="text-purple-600 font-medium">Actualizado:</span>
                          <span className="text-muted-foreground">{tipo.lastUpdated}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-1 ml-4">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleViewDetails(tipo)}
                        title="Ver detalles"
                      >
                        <Eye className="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleEdit(tipo)}
                        title="Editar"
                      >
                        <Edit className="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDelete(tipo)}
                        title="Eliminar"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              
              {filteredTiposEquipo.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Wrench className="mx-auto h-12 w-12 text-muted-foreground/50" />
                  <h3 className="mt-2 text-sm font-medium">No se encontraron tipos de equipo</h3>
                  <p className="mt-1 text-sm">No hay tipos de equipo que coincidan con el término de búsqueda.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </ContentGrid>

      {/* Formulario de creación de tipo de equipo */}
      <CreateTipoEquipoForm
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={() => {
          fetchData();
        }}
      />

      {/* Formulario de edición de tipo de equipo */}
      {selectedTipo && (
        <CreateTipoEquipoForm
          isOpen={showEditForm}
          onClose={() => {
            setShowEditForm(false);
            setSelectedTipo(null);
          }}
          onSuccess={() => {
            fetchData();
            setShowEditForm(false);
            setSelectedTipo(null);
          }}
          tipoEquipoData={selectedTipo}
        />
      )}

      {/* Diálogo de confirmación de eliminación */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Estás seguro?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará permanentemente el tipo de equipo "{selectedTipo?.name}".
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

export default TiposEquipoView;