import React, { useState, useEffect, useMemo } from 'react';
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
import EquipmentDetailPanel from '@/components/equipment/EquipmentDetailPanel';
import { equiposService } from '@/services/apiService';

// Nota: Usando el servicio centralizado equiposService en lugar de crear un cliente axios local

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
  const [marcaFilter, setMarcaFilter] = useState('all');
  const [faenaFilter, setFaenaFilter] = useState('all');
  const [sortConfig, setSortConfig] = useState<{ key: SortKey; direction: 'asc' | 'desc' } | null>(null);
  const [selectedEquipo, setSelectedEquipo] = useState<Equipo | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDetailPanel, setShowDetailPanel] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError('');
        
        // Cargar equipos desde el backend
        const response = await equiposService.getAll();
        const equiposData = response.results || response.data || response;
        
        // Mapear datos del backend al formato del componente
        const mappedEquipos: Equipo[] = equiposData.map((eq: any) => ({
          id: eq.idequipo,
          codigo: eq.codigointerno || `EQ-${eq.idequipo}`,
          nombre: eq.nombreequipo,
          marca: eq.marca || 'N/A',
          modelo: eq.modelo || 'N/A',
          patente: eq.patente || 'N/A',
          ubicacion: eq.faena_nombre || eq.idfaenaactual?.nombrefaena || eq.ubicacion || 'Sin ubicación',
          estado: eq.estado_nombre || eq.idestadoactual?.nombreestado || 'Desconocido',
          categoria: eq.tipo_equipo_nombre || eq.idtipoequipo?.nombretipo || 'Sin categoría',
          ultimoMantenimiento: eq.ultima_mantenimiento || eq.fechaultimoMantenimiento || 'N/A',
          activo: eq.activo !== false
        }));
        
        setEquipos(mappedEquipos);
        
        // Calcular estadísticas
        const stats: EquipmentStats = {
          total: mappedEquipos.length,
          operativos: mappedEquipos.filter(e => e.estado === 'Operativo').length,
          enMantenimiento: mappedEquipos.filter(e => e.estado.includes('Mantenimiento')).length,
          fueraServicio: mappedEquipos.filter(e => e.estado === 'Fuera de Servicio').length
        };
        
        setStats(stats);
        
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
        equipo.patente.toLowerCase().includes(searchTerm.toLowerCase()) ||
        equipo.marca.toLowerCase().includes(searchTerm.toLowerCase()) ||
        equipo.modelo.toLowerCase().includes(searchTerm.toLowerCase())
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

    // Filtrar por marca
    if (marcaFilter !== 'all') {
      filtered = filtered.filter(equipo => equipo.marca === marcaFilter);
    }

    // Filtrar por faena
    if (faenaFilter !== 'all') {
      filtered = filtered.filter(equipo => equipo.ubicacion === faenaFilter);
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
  }, [equipos, searchTerm, categoriaFilter, estadoFilter, marcaFilter, faenaFilter, sortConfig]);

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
    setShowDetailPanel(true);
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
            <div className="flex flex-col gap-4">
              <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
                <div>
                  <CardTitle>Lista de Equipos</CardTitle>
                  <CardDescription>
                    Mostrando {filteredEquipos.length} de {equipos.length} equipos
                  </CardDescription>
                </div>
                
                {(searchTerm || categoriaFilter !== 'all' || marcaFilter !== 'all' || faenaFilter !== 'all' || estadoFilter !== 'all') && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => {
                      setSearchTerm('');
                      setCategoriaFilter('all');
                      setMarcaFilter('all');
                      setFaenaFilter('all');
                      setEstadoFilter('all');
                    }}
                  >
                    <Filter className="h-4 w-4 mr-2" />
                    Limpiar Filtros
                  </Button>
                )}
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
                  <SelectTrigger className="w-full md:w-40">
                    <SelectValue placeholder="Tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los tipos</SelectItem>
                    <SelectItem value="Camionetas">Camionetas</SelectItem>
                    <SelectItem value="Retroexcavadora">Retroexcavadora</SelectItem>
                    <SelectItem value="Cargador Frontal">Cargador Frontal</SelectItem>
                    <SelectItem value="Minicargador">Minicargador</SelectItem>
                    <SelectItem value="Camion Supersucker">Camión Supersucker</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={marcaFilter} onValueChange={setMarcaFilter}>
                  <SelectTrigger className="w-full md:w-40">
                    <SelectValue placeholder="Marca" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas las marcas</SelectItem>
                    <SelectItem value="Toyota">Toyota</SelectItem>
                    <SelectItem value="Caterpillar">Caterpillar</SelectItem>
                    <SelectItem value="Komatsu">Komatsu</SelectItem>
                    <SelectItem value="Case">Case</SelectItem>
                    <SelectItem value="John Deere">John Deere</SelectItem>
                    <SelectItem value="JCB">JCB</SelectItem>
                    <SelectItem value="Nissan">Nissan</SelectItem>
                    <SelectItem value="Mitsubishi">Mitsubishi</SelectItem>
                    <SelectItem value="Chevrolet">Chevrolet</SelectItem>
                    <SelectItem value="Bobcat">Bobcat</SelectItem>
                    <SelectItem value="Gehl">Gehl</SelectItem>
                    <SelectItem value="Kenworth">Kenworth</SelectItem>
                    <SelectItem value="Peterbilt">Peterbilt</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={faenaFilter} onValueChange={setFaenaFilter}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Faena" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas las faenas</SelectItem>
                    <SelectItem value="Faena Central Santiago">Faena Central Santiago</SelectItem>
                    <SelectItem value="Faena Norte Antofagasta">Faena Norte Antofagasta</SelectItem>
                    <SelectItem value="Faena Sur Concepcion">Faena Sur Concepción</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={estadoFilter} onValueChange={setEstadoFilter}>
                  <SelectTrigger className="w-full md:w-40">
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
                        Equipo {getSortIcon('nombre')}
                      </div>
                    </th>
                    <th 
                      className="text-left p-4 font-medium cursor-pointer hover:bg-muted/50"
                      onClick={() => requestSort('marca')}
                    >
                      <div className="flex items-center gap-2">
                        Marca {getSortIcon('marca')}
                      </div>
                    </th>
                    <th 
                      className="text-left p-4 font-medium cursor-pointer hover:bg-muted/50"
                      onClick={() => requestSort('modelo')}
                    >
                      <div className="flex items-center gap-2">
                        Modelo {getSortIcon('modelo')}
                      </div>
                    </th>
                    <th 
                      className="text-left p-4 font-medium cursor-pointer hover:bg-muted/50"
                      onClick={() => requestSort('patente')}
                    >
                      <div className="flex items-center gap-2">
                        Patente {getSortIcon('patente')}
                      </div>
                    </th>
                    <th 
                      className="text-left p-4 font-medium cursor-pointer hover:bg-muted/50"
                      onClick={() => requestSort('categoria')}
                    >
                      <div className="flex items-center gap-2">
                        Tipo {getSortIcon('categoria')}
                      </div>
                    </th>
                    <th 
                      className="text-left p-4 font-medium cursor-pointer hover:bg-muted/50"
                      onClick={() => requestSort('ubicacion')}
                    >
                      <div className="flex items-center gap-2">
                        Faena {getSortIcon('ubicacion')}
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
                    <th className="text-center p-4 font-medium">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredEquipos.map((equipo) => (
                    <tr key={equipo.id} className="border-b hover:bg-muted/50">
                      <td className="p-4">
                        <div className="font-mono text-sm font-bold text-primary">
                          {equipo.codigo}
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="font-medium">{equipo.nombre}</div>
                      </td>
                      <td className="p-4">
                        <div className="text-sm">{equipo.marca}</div>
                      </td>
                      <td className="p-4">
                        <div className="text-sm">{equipo.modelo}</div>
                      </td>
                      <td className="p-4">
                        <div className="font-mono text-sm font-semibold">
                          {equipo.patente}
                        </div>
                      </td>
                      <td className="p-4">
                        <Badge variant="outline" className="text-xs">
                          {equipo.categoria}
                        </Badge>
                      </td>
                      <td className="p-4">
                        <div className="text-sm">{equipo.ubicacion}</div>
                      </td>
                      <td className="p-4">{getStatusBadge(equipo.estado)}</td>
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

      {/* Panel de detalles del equipo */}
      {showDetailPanel && selectedEquipo && (
        <EquipmentDetailPanel
          equipo={selectedEquipo}
          onClose={() => {
            setShowDetailPanel(false);
            setSelectedEquipo(null);
          }}
        />
      )}
    </PageLayout>
  );
};

export default EstadoMaquinaView;
