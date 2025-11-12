import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Plus, 
  Search, 
  Filter,
  MapPin,
  Phone,
  Mail,
  CheckCircle,
  XCircle,
  Edit,
  Trash2,
  Eye,
  Users,
  Wrench,
  Calendar
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import CreateFaenaForm from '@/components/forms/CreateFaenaForm';
import { faenasService } from '@/services/faenasService';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface Faena {
  id: number;
  name: string;
  location: string;
  contact: string;
  phone: string;
  email: string;
  isActive: boolean;
  equipmentCount: number;
  technicianCount: number;
  lastMaintenance: string;
  createdAt: string;
}

interface FaenaStats {
  totalFaenas: number;
  activeFaenas: number;
  inactiveFaenas: number;
  totalEquipment: number;
  totalTechnicians: number;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

const FaenasView: React.FC = () => {
  const [faenas, setFaenas] = useState<Faena[]>([]);
  const [stats, setStats] = useState<FaenaStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedFaena, setSelectedFaena] = useState<Faena | null>(null);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Cargar datos reales del backend
      const response = await faenasService.getAll();
      const faenasData = response.results || response || [];
      
      // Transformar datos del backend
      const faenasTransformadas = faenasData.map((faena: any) => ({
        id: faena.idfaena,
        name: faena.nombrefaena,
        location: `${faena.ciudad || ''}, ${faena.region || ''}`.trim() || faena.ubicacion || 'Sin ubicación',
        contact: faena.contacto || 'Sin contacto',
        phone: faena.telefono || 'Sin teléfono',
        email: faena.email || 'Sin email',
        isActive: faena.activa !== undefined ? faena.activa : true,
        equipmentCount: faena.equipos_count || 0,
        technicianCount: faena.tecnicos_count || 0,
        lastMaintenance: faena.ultimo_mantenimiento || 'N/A',
        createdAt: faena.fechacreacion || new Date().toISOString().split('T')[0]
      }));
      
      setFaenas(faenasTransformadas);
      
      // Calcular estadísticas
      const activeFaenas = faenasTransformadas.filter((f: any) => f.isActive).length;
      const totalEquipment = faenasTransformadas.reduce((sum: number, f: any) => sum + f.equipmentCount, 0);
      const totalTechnicians = faenasTransformadas.reduce((sum: number, f: any) => sum + f.technicianCount, 0);
      
      setStats({
        totalFaenas: faenasTransformadas.length,
        activeFaenas,
        inactiveFaenas: faenasTransformadas.length - activeFaenas,
        totalEquipment,
        totalTechnicians
      });
      
      console.log('✅ Faenas cargadas:', faenasTransformadas.length);
    } catch (err) {
      console.error("Error fetching faenas data:", err);
      setError("No se pudo cargar la información de faenas.");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (faena: Faena) => {
    setSelectedFaena(faena);
    setShowEditForm(true);
  };

  const handleDelete = (faena: Faena) => {
    setSelectedFaena(faena);
    setShowDeleteDialog(true);
  };

  const confirmDelete = async () => {
    if (!selectedFaena) return;
    
    try {
      await faenasService.delete(selectedFaena.id);
      console.log('✅ Faena eliminada:', selectedFaena.name);
      setShowDeleteDialog(false);
      setSelectedFaena(null);
      await fetchData();
    } catch (err) {
      console.error('❌ Error eliminando faena:', err);
      setError('Error al eliminar la faena');
    }
  };

  const handleSuccess = () => {
    fetchData();
    setSelectedFaena(null);
  };

  // Filtrar faenas
  const filteredFaenas = faenas.filter(faena => {
    const matchesSearch = faena.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         faena.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         faena.contact.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'active' && faena.isActive) ||
                         (statusFilter === 'inactive' && !faena.isActive);
    
    return matchesSearch && matchesStatus;
  });

  // Obtener badge de estado
  const getStatusBadge = (isActive: boolean) => {
    return isActive ? (
      <Badge variant="default" className="bg-green-100 text-green-800">
        <CheckCircle className="h-3 w-3 mr-1" />Activa
      </Badge>
    ) : (
      <Badge variant="destructive">
        <XCircle className="h-3 w-3 mr-1" />Inactiva
      </Badge>
    );
  };

  // Handlers para acciones
  const handleViewDetails = (faena: Faena) => {
    setSelectedFaena(faena);
    // Aquí podrías abrir un modal de detalles
    console.log('Ver detalles de:', faena.name);
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
        title="Gestión de Faenas" 
        subtitle="Administración de ubicaciones y sitios de trabajo"
      >
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nueva Faena
        </Button>
      </PageHeader>

      {/* Tarjetas de estadísticas */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Faenas</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalFaenas}</div>
            <p className="text-xs text-muted-foreground">
              Ubicaciones registradas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Faenas Activas</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.activeFaenas}</div>
            <p className="text-xs text-muted-foreground">
              {stats ? Math.round((stats.activeFaenas / stats.totalFaenas) * 100) : 0}% del total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Equipos</CardTitle>
            <Wrench className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.totalEquipment}</div>
            <p className="text-xs text-muted-foreground">
              Equipos distribuidos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Técnicos</CardTitle>
            <Users className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{stats?.totalTechnicians}</div>
            <p className="text-xs text-muted-foreground">
              Personal técnico asignado
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Lista de faenas */}
      <ContentGrid>
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
              <div>
                <CardTitle>Lista de Faenas</CardTitle>
                <CardDescription>
                  Ubicaciones y sitios de trabajo del sistema
                </CardDescription>
              </div>
              
              <div className="flex flex-col md:flex-row gap-2 w-full md:w-auto">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar faena..."
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
                    <SelectItem value="active">Activas</SelectItem>
                    <SelectItem value="inactive">Inactivas</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredFaenas.map(faena => (
                <div key={faena.id} className="border rounded-lg p-4 hover:bg-muted/50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-medium">{faena.name}</h4>
                        {getStatusBadge(faena.isActive)}
                      </div>
                      
                      <div className="text-sm text-muted-foreground space-y-1">
                        <div className="flex items-center gap-2">
                          <MapPin className="h-3 w-3" />
                          {faena.location}
                        </div>
                        <div className="flex items-center gap-2">
                          <Users className="h-3 w-3" />
                          Contacto: {faena.contact}
                        </div>
                        <div className="flex items-center gap-2">
                          <Phone className="h-3 w-3" />
                          {faena.phone}
                        </div>
                        <div className="flex items-center gap-2">
                          <Mail className="h-3 w-3" />
                          {faena.email}
                        </div>
                      </div>
                      
                      <div className="flex gap-4 mt-3 text-sm">
                        <div className="flex items-center gap-1">
                          <Wrench className="h-3 w-3 text-blue-600" />
                          <span className="text-blue-600 font-medium">{faena.equipmentCount}</span>
                          <span className="text-muted-foreground">equipos</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Users className="h-3 w-3 text-purple-600" />
                          <span className="text-purple-600 font-medium">{faena.technicianCount}</span>
                          <span className="text-muted-foreground">técnicos</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3 text-green-600" />
                          <span className="text-green-600 font-medium">Último mantenimiento:</span>
                          <span className="text-muted-foreground">{faena.lastMaintenance}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-1 ml-4">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleViewDetails(faena)}
                        title="Ver detalles"
                      >
                        <Eye className="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleEdit(faena)}
                        title="Editar"
                      >
                        <Edit className="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDelete(faena)}
                        title="Eliminar"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              
              {filteredFaenas.length === 0 && faenas.length === 0 && (
                <div className="text-center py-12 text-muted-foreground">
                  <Building2 className="mx-auto h-16 w-16 text-muted-foreground/30 mb-4" />
                  <h3 className="text-lg font-medium mb-2">No hay faenas registradas</h3>
                  <p className="text-sm mb-4">Comienza creando la primera faena o sitio de trabajo.</p>
                  <Button onClick={() => setShowCreateForm(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Crear Primera Faena
                  </Button>
                </div>
              )}
              
              {filteredFaenas.length === 0 && faenas.length > 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Search className="mx-auto h-12 w-12 text-muted-foreground/50" />
                  <h3 className="mt-2 text-sm font-medium">No se encontraron resultados</h3>
                  <p className="mt-1 text-sm">No hay faenas que coincidan con los filtros seleccionados.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </ContentGrid>

      {/* Formulario de creación de faena */}
      <CreateFaenaForm
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={() => {
          // Recargar datos después de crear
          fetchData();
        }}
      />

      {/* Formulario de edición de faena */}
      {selectedFaena && (
        <CreateFaenaForm
          isOpen={showEditForm}
          onClose={() => {
            setShowEditForm(false);
            setSelectedFaena(null);
          }}
          onSuccess={() => {
            fetchData();
            setShowEditForm(false);
            setSelectedFaena(null);
          }}
          faenaData={selectedFaena}
        />
      )}

      {/* Diálogo de confirmación de eliminación */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Estás seguro?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará permanentemente la faena "{selectedFaena?.name}".
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

export default FaenasView;