import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { 
  Server, 
  Zap, 
  ZapOff, 
  Search, 
  ChevronDown, 
  ChevronUp,
  Wrench,
  AlertTriangle,
  CheckCircle,
  Clock,
  Filter,
  Plus
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import CreateEquipmentForm from '@/components/forms/CreateEquipmentForm';

// =================================================================================
// CONFIGURACIÓN DE API
// =================================================================================

const API_URL = 'http://localhost:8000/api';
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
}, error => Promise.reject(error));

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

interface EquipmentStats {
  total: number;
  operativos: number;
  enMantenimiento: number;
  fueraServicio: number;
}

type SortKey = keyof Equipo;

const EstadoMaquinaView: React.FC = () => {
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [stats, setStats] = useState<EquipmentStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoriaFilter, setCategoriaFilter] = useState('all');
  const [estadoFilter, setEstadoFilter] = useState('all');
  const [sortConfig, setSortConfig] = useState<{ key: SortKey; direction: 'asc' | 'desc' } | null>(null);
  const [selectedEquipo, setSelectedEquipo] = useState<Equipo | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);

  // Datos de ejemplo para el diseño
  const mockEquipos: Equipo[] = [
    {
      id: 1,
      codigo: "EQ-001",
      nombre: "Compresor de Aire Principal",
      marca: "Atlas Copco",
      modelo: "GA 37",
      patente: "ABC-123",
      ubicacion: "Planta Norte",
      estado: "Operativo",
      categoria: "Compresores",
      ultimoMantenimiento: "15-09-2024",
      activo: true
    },
    {
      id: 2,
      codigo: "EQ-002",
      nombre: "Bomba Centrífuga B-205",
      marca: "Grundfos",
      modelo: "CR 32-4",
      patente: "DEF-456",
      ubicacion: "Planta Sur",
      estado: "En Mantenimiento",
      categoria: "Bombas",
      ultimoMantenimiento: "20-09-2024",
      activo: true
    },
    {
      id: 3,
      codigo: "EQ-003",
      nombre: "Motor Eléctrico C-310",
      marca: "Siemens",
      modelo: "1LA7 090-4",
      patente: "GHI-789",
      ubicacion: "Planta Central",
      estado: "Fuera de Servicio",
      categoria: "Motores",
      ultimoMantenimiento: "10-08-2024",
      activo: true
    },
    {
      id: 4,
      codigo: "EQ-004",
      nombre: "Válvula de Control D-115",
      marca: "Fisher",
      modelo: "V150",
      patente: "JKL-012",
      ubicacion: "Planta Este",
      estado: "Operativo",
      categoria: "Válvulas",
      ultimoMantenimiento: "25-09-2024",
      activo: true
    }
  ];

  const mockStats: EquipmentStats = {
    total: 156,
    operativos: 142,
    enMantenimiento: 8,
    fueraServicio: 6
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Usar datos mock por ahora
        setEquipos(mockEquipos);
        setStats(mockStats);
        setError('');
      } catch (err) {
        console.error("Error fetching equipment data:", err);
        setError("No se pudo cargar la información de los equipos.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredEquipos = useMemo(() => {
    let filtered = equipos;

    // Filtrar por búsqueda
    if (searchTerm) {
      filtered = filtered.filter(equipo =>
        equipo.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
        equipo.codigo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        equipo.patente.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filtrar por categoría
    if (categoriaFilter !== 'all') {
      filtered = filtered.filter(equipo => equipo.categoria === categoriaFilter);
    }

    // Filtrar por estado
    if (estadoFilter !== 'all') {
      filtered = filtered.filter(equipo => equipo.estado === estadoFilter);
    }

    // Ordenar
    if (sortConfig) {
      filtered.sort((a, b) => {
        const aVal = a[sortConfig.key];
        const bVal = b[sortConfig.key];
        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return filtered;
  }, [equipos, searchTerm, categoriaFilter, estadoFilter, sortConfig]);

  const requestSort = (key: SortKey) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const getSortIcon = (key: SortKey) => {
    if (!sortConfig || sortConfig.key !== key) {
      return <ChevronDown className="h-4 w-4 text-muted-foreground" />;
    }
    return sortConfig.direction === 'asc' ? 
      <ChevronUp className="h-4 w-4" /> : 
      <ChevronDown className="h-4 w-4" />;
  };

  const getStatusBadge = (estado: string) => {
    switch (estado) {
      case 'Operativo':
        return <Badge variant="default" className="bg-green-100 text-green-800 hover:bg-green-200"><CheckCircle className="h-3 w-3 mr-1" />Operativo</Badge>;
      case 'En Mantenimiento':
        return <Badge variant="default" className="bg-blue-100 text-blue-800 hover:bg-blue-200"><Wrench className="h-3 w-3 mr-1" />En Mantenimiento</Badge>;
      case 'Fuera de Servicio':
        return <Badge variant="destructive"><AlertTriangle className="h-3 w-3 mr-1" />Fuera de Servicio</Badge>;
      default:
        return <Badge variant="secondary"><Clock className="h-3 w-3 mr-1" />{estado}</Badge>;
    }
  };

  // Handlers para acciones
  const handleViewDetails = (equipo: Equipo) => {
    setSelectedEquipo(equipo);
    console.log('Ver detalles de:', equipo.nombre);
  };

  const handleEdit = (equipo: Equipo) => {
    setSelectedEquipo(equipo);
    setShowEditForm(true);
  };

  const handleDelete = (equipo: Equipo) => {
    setSelectedEquipo(equipo);
    setShowDeleteDialog(true);
  };

  const confirmDelete = () => {
    if (selectedEquipo) {
      console.log('Eliminar equipo:', selectedEquipo.nombre);
      setShowDeleteDialog(false);
      setSelectedEquipo(null);
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
        title="Estado de Máquinas" 
        subtitle="Monitoreo y gestión del estado de equipos industriales"
      >
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Equipo
        </Button>
      </PageHeader>

      {/* Tarjetas de estadísticas */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Equipos</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total}</div>
            <p className="text-xs text-muted-foreground">
              Equipos registrados en el sistema
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Operativos</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.operativos}</div>
            <p className="text-xs text-muted-foreground">
              {stats ? Math.round((stats.operativos / stats.total) * 100) : 0}% del total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">En Mantenimiento</CardTitle>
            <Wrench className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.enMantenimiento}</div>
            <p className="text-xs text-muted-foreground">
              Requieren atención
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Fuera de Servicio</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{stats?.fueraServicio}</div>
            <p className="text-xs text-muted-foreground">
              Requieren reparación urgente
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Tabla de equipos */}
      <ContentGrid>
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
              <div>
                <CardTitle>Lista de Equipos</CardTitle>
                <CardDescription>
                  Estado actual de todos los equipos industriales
                </CardDescription>
              </div>
              
              <div className="flex flex-col md:flex-row gap-2 w-full md:w-auto">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar equipo..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-full md:w-64"
                  />
                </div>
                
                <Select value={categoriaFilter} onValueChange={setCategoriaFilter}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Categoría" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas las categorías</SelectItem>
                    <SelectItem value="Compresores">Compresores</SelectItem>
                    <SelectItem value="Bombas">Bombas</SelectItem>
                    <SelectItem value="Motores">Motores</SelectItem>
                    <SelectItem value="Válvulas">Válvulas</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={estadoFilter} onValueChange={setEstadoFilter}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Estado" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los estados</SelectItem>
                    <SelectItem value="Operativo">Operativo</SelectItem>
                    <SelectItem value="En Mantenimiento">En Mantenimiento</SelectItem>
                    <SelectItem value="Fuera de Servicio">Fuera de Servicio</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th 
                      className="text-left p-4 font-medium cursor-pointer hover:bg-muted/50"
                      onClick={() => requestSort('codigo')}
                    >
                      <div className="flex items-center gap-2">
                        Código {getSortIcon('codigo')}
                      </div>
                    </th>
                    <th 
                      className="text-left p-4 font-medium cursor-pointer hover:bg-muted/50"
                      onClick={() => requestSort('nombre')}
                    >
                      <div className="flex items-center gap-2">
                        Nombre {getSortIcon('nombre')}
                      </div>
                    </th>
                    <th 
                      className="text-left p-4 font-medium cursor-pointer hover:bg-muted/50"
                      onClick={() => requestSort('categoria')}
                    >
                      <div className="flex items-center gap-2">
                        Categoría {getSortIcon('categoria')}
                      </div>
                    </th>
                    <th 
                      className="text-left p-4 font-medium cursor-pointer hover:bg-muted/50"
                      onClick={() => requestSort('ubicacion')}
                    >
                      <div className="flex items-center gap-2">
                        Ubicación {getSortIcon('ubicacion')}
                      </div>
                    </th>
                    <th 
                      className="text-left p-4 font-medium cursor-pointer hover:bg-muted/50"
                      onClick={() => requestSort('estado')}
                    >
                      <div className="flex items-center gap-2">
                        Estado {getSortIcon('estado')}
                      </div>
                    </th>
                    <th className="text-left p-4 font-medium">Último Mantenimiento</th>
                    <th className="text-center p-4 font-medium">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredEquipos.map((equipo) => (
                    <tr key={equipo.id} className="border-b hover:bg-muted/50">
                      <td className="p-4 font-medium">{equipo.codigo}</td>
                      <td className="p-4">
                        <div>
                          <div className="font-medium">{equipo.nombre}</div>
                          <div className="text-sm text-muted-foreground">
                            {equipo.marca} {equipo.modelo}
                          </div>
                        </div>
                      </td>
                      <td className="p-4">{equipo.categoria}</td>
                      <td className="p-4">{equipo.ubicacion}</td>
                      <td className="p-4">{getStatusBadge(equipo.estado)}</td>
                      <td className="p-4 text-sm text-muted-foreground">
                        {equipo.ultimoMantenimiento}
                      </td>
                      <td className="p-4">
                        <div className="flex justify-center gap-2">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => handleViewDetails(equipo)}
                          >
                            Ver
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => handleEdit(equipo)}
                          >
                            Editar
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {filteredEquipos.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Server className="mx-auto h-12 w-12 text-muted-foreground/50" />
                  <h3 className="mt-2 text-sm font-medium">No se encontraron equipos</h3>
                  <p className="mt-1 text-sm">Pruebe a cambiar los filtros o el término de búsqueda.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </ContentGrid>

      {/* Formulario de creación de equipo */}
      <CreateEquipmentForm
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={() => {
          console.log('Equipo creado exitosamente');
        }}
      />

      {/* Formulario de edición de equipo */}
      {selectedEquipo && (
        <CreateEquipmentForm
          isOpen={showEditForm}
          onClose={() => {
            setShowEditForm(false);
            setSelectedEquipo(null);
          }}
          onSuccess={() => {
            console.log('Equipo actualizado exitosamente');
            setShowEditForm(false);
            setSelectedEquipo(null);
          }}
          equipmentData={selectedEquipo}
        />
      )}

      {/* Diálogo de confirmación de eliminación */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Estás seguro?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará permanentemente el equipo "{selectedEquipo?.nombre}".
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

export default EstadoMaquinaView;
