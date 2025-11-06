import React, { useState, useEffect } from 'react';
import { 
  ClipboardList, 
  Plus, 
  Search, 
  Filter,
  Settings,
  Edit,
  Trash2,
  Eye,
  Clock,
  CheckCircle,
  AlertTriangle,
  Wrench,
  FileText,
  Calendar
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import CreateTaskTypeForm from '@/components/forms/CreateTaskTypeForm';
import { tiposTareaService } from '@/services/tiposTareaService';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface TipoTarea {
  id: number;
  name: string;
  description: string;
  category: 'preventivo' | 'correctivo' | 'predictivo' | 'inspeccion';
  estimatedDuration: string;
  difficulty: 'baja' | 'media' | 'alta';
  isActive: boolean;
  taskCount: number;
  createdAt: string;
  lastUpdated: string;
}

interface TipoTareaStats {
  totalTipos: number;
  activeTipos: number;
  totalTasks: number;
  mostUsedType: string;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

const TiposTareaView: React.FC = () => {
  const [tiposTarea, setTiposTarea] = useState<TipoTarea[]>([]);
  const [stats, setStats] = useState<TipoTareaStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTipo, setSelectedTipo] = useState<TipoTarea | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);

  // Datos de ejemplo para el diseño
  const mockTiposTarea: TipoTarea[] = [
    {
      id: 1,
      name: 'Cambio de Filtros',
      description: 'Reemplazo de filtros de aire, aceite y combustible según especificaciones',
      category: 'preventivo',
      estimatedDuration: '2 horas',
      difficulty: 'baja',
      isActive: true,
      taskCount: 45,
      createdAt: '2024-01-15',
      lastUpdated: '2024-10-15'
    },
    {
      id: 2,
      name: 'Reparación de Sello Mecánico',
      description: 'Desmontaje, inspección y reemplazo de sellos mecánicos en bombas',
      category: 'correctivo',
      estimatedDuration: '4 horas',
      difficulty: 'alta',
      isActive: true,
      taskCount: 18,
      createdAt: '2024-02-20',
      lastUpdated: '2024-10-14'
    },
    {
      id: 3,
      name: 'Análisis de Vibraciones',
      description: 'Medición y análisis de vibraciones en equipos rotativos',
      category: 'predictivo',
      estimatedDuration: '3 horas',
      difficulty: 'media',
      isActive: true,
      taskCount: 32,
      createdAt: '2024-03-10',
      lastUpdated: '2024-10-13'
    },
    {
      id: 4,
      name: 'Inspección Visual',
      description: 'Inspección visual general de equipos y componentes',
      category: 'inspeccion',
      estimatedDuration: '1 hora',
      difficulty: 'baja',
      isActive: true,
      taskCount: 67,
      createdAt: '2024-04-15',
      lastUpdated: '2024-10-12'
    },
    {
      id: 5,
      name: 'Calibración de Instrumentos',
      description: 'Calibración de instrumentos de medición y control',
      category: 'preventivo',
      estimatedDuration: '2.5 horas',
      difficulty: 'media',
      isActive: false,
      taskCount: 12,
      createdAt: '2024-05-20',
      lastUpdated: '2024-09-20'
    }
  ];

  const mockStats: TipoTareaStats = {
    totalTipos: 15,
    activeTipos: 12,
    totalTasks: 234,
    mostUsedType: 'Inspección Visual'
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Usar datos mock por ahora
        setTiposTarea(mockTiposTarea);
        setStats(mockStats);
        setError('');
      } catch (err) {
        console.error("Error fetching task types data:", err);
        setError("No se pudo cargar la información de tipos de tarea.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filtrar tipos de tarea
  const filteredTiposTarea = tiposTarea.filter(tipo => {
    return tipo.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           tipo.description.toLowerCase().includes(searchTerm.toLowerCase());
  });

  // Obtener badge de categoría
  const getCategoryBadge = (category: string) => {
    switch (category) {
      case 'preventivo':
        return <Badge variant="default" className="bg-blue-100 text-blue-800">Preventivo</Badge>;
      case 'correctivo':
        return <Badge variant="default" className="bg-orange-100 text-orange-800">Correctivo</Badge>;
      case 'predictivo':
        return <Badge variant="default" className="bg-green-100 text-green-800">Predictivo</Badge>;
      case 'inspeccion':
        return <Badge variant="default" className="bg-purple-100 text-purple-800">Inspección</Badge>;
      default:
        return <Badge variant="secondary">{category}</Badge>;
    }
  };

  // Obtener badge de dificultad
  const getDifficultyBadge = (difficulty: string) => {
    switch (difficulty) {
      case 'baja':
        return <Badge variant="default" className="bg-green-100 text-green-800">Baja</Badge>;
      case 'media':
        return <Badge variant="default" className="bg-yellow-100 text-yellow-800">Media</Badge>;
      case 'alta':
        return <Badge variant="destructive">Alta</Badge>;
      default:
        return <Badge variant="secondary">{difficulty}</Badge>;
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

  // Handlers para acciones
  const handleViewDetails = (tipo: TipoTarea) => {
    setSelectedTipo(tipo);
    console.log('Ver detalles de:', tipo.name);
  };

  const handleEdit = (tipo: TipoTarea) => {
    setSelectedTipo(tipo);
    setShowEditForm(true);
  };

  const handleDelete = (tipo: TipoTarea) => {
    setSelectedTipo(tipo);
    setShowDeleteDialog(true);
  };

  const confirmDelete = () => {
    if (selectedTipo) {
      console.log('Eliminar tipo de tarea:', selectedTipo.name);
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
        title="Tipos de Tarea" 
        subtitle="Configuración y gestión de categorías de tareas de mantenimiento"
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
            <ClipboardList className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalTipos}</div>
            <p className="text-xs text-muted-foreground">
              Tipos de tarea registrados
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
            <CardTitle className="text-sm font-medium">Total Tareas</CardTitle>
            <FileText className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.totalTasks}</div>
            <p className="text-xs text-muted-foreground">
              Tareas categorizadas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tipo Más Usado</CardTitle>
            <Settings className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{stats?.mostUsedType}</div>
            <p className="text-xs text-muted-foreground">
              Categoría principal
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Lista de tipos de tarea */}
      <ContentGrid>
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
              <div>
                <CardTitle>Lista de Tipos de Tarea</CardTitle>
                <CardDescription>
                  Categorías y configuraciones de tareas de mantenimiento
                </CardDescription>
              </div>
              
              <div className="flex flex-col md:flex-row gap-2 w-full md:w-auto">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar tipo de tarea..."
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
              {filteredTiposTarea.map(tipo => (
                <div key={tipo.id} className="border rounded-lg p-4 hover:bg-muted/50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-medium">{tipo.name}</h4>
                        {getStatusBadge(tipo.isActive)}
                        {getCategoryBadge(tipo.category)}
                        {getDifficultyBadge(tipo.difficulty)}
                      </div>
                      
                      <p className="text-sm text-muted-foreground mb-3">
                        {tipo.description}
                      </p>
                      
                      <div className="flex gap-4 text-sm">
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3 text-blue-600" />
                          <span className="text-blue-600 font-medium">Duración:</span>
                          <span className="text-muted-foreground">{tipo.estimatedDuration}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <FileText className="h-3 w-3 text-green-600" />
                          <span className="text-green-600 font-medium">{tipo.taskCount}</span>
                          <span className="text-muted-foreground">tareas</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3 text-purple-600" />
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
              
              {filteredTiposTarea.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <ClipboardList className="mx-auto h-12 w-12 text-muted-foreground/50" />
                  <h3 className="mt-2 text-sm font-medium">No se encontraron tipos de tarea</h3>
                  <p className="mt-1 text-sm">No hay tipos de tarea que coincidan con el término de búsqueda.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </ContentGrid>

      {/* Formulario de creación de tipo de tarea */}
      <CreateTaskTypeForm
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={() => {
          console.log('Tipo de tarea creado exitosamente');
        }}
      />

      {/* Formulario de edición de tipo de tarea */}
      {selectedTipo && (
        <CreateTaskTypeForm
          isOpen={showEditForm}
          onClose={() => {
            setShowEditForm(false);
            setSelectedTipo(null);
          }}
          onSuccess={() => {
            console.log('Tipo de tarea actualizado exitosamente');
            setShowEditForm(false);
            setSelectedTipo(null);
          }}
          taskTypeData={selectedTipo}
        />
      )}

      {/* Diálogo de confirmación de eliminación */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Estás seguro?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará permanentemente el tipo de tarea "{selectedTipo?.name}".
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

export default TiposTareaView;