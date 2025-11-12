import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Users, 
  UserCheck, 
  Briefcase, 
  Wrench,
  Mail,
  Phone,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import CreateTecnicoForm from '@/components/forms/CreateTecnicoForm';
import { tecnicosService } from '@/services/tecnicosService';

interface Technician {
  id: string;
  name: string;
  email: string;
  phone: string;
  status: 'available' | 'busy' | 'offline';
  activeOrders: number;
  specialties: string[];
  avatar: string;
}

const TecnicosView: React.FC = () => {
  const [technicians, setTechnicians] = useState<Technician[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('all');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedTechnician, setSelectedTechnician] = useState<Technician | null>(null);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  // Datos de ejemplo para el diseño
  const mockStats = {
    total: 3,
    available: 1,
    busy: 2,
    offline: 0
  };

  const mockTechnicians: Technician[] = [
    {
      id: "1",
      name: "Juan Pérez",
      email: "juan.perez@somacor.com",
      phone: "+56 9 1234 5678",
      status: "busy",
      activeOrders: 2,
      specialties: ["Compresores", "Sistemas Neumáticos", "Mantenimiento Preventivo"],
      avatar: "JP"
    },
    {
      id: "2",
      name: "María García",
      email: "maria.garcia@somacor.com",
      phone: "+56 9 2345 6789",
      status: "busy",
      activeOrders: 1,
      specialties: ["Bombas Centrífugas", "Sistemas Hidráulicos"],
      avatar: "MG"
    },
    {
      id: "3",
      name: "Carlos López",
      email: "carlos.lopez@somacor.com",
      phone: "+56 9 3456 7890",
      status: "available",
      activeOrders: 0,
      specialties: ["Motores Eléctricos", "Sistemas Eléctricos", "Automatización"],
      avatar: "CL"
    }
  ];

  useEffect(() => {
    fetchTechnicians();
  }, []);

  const fetchTechnicians = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await tecnicosService.getAll();
      const tecnicos = response.results || response || [];
      
      const tecnicosTransformados = tecnicos.map((tec: any) => ({
        id: tec.user?.id?.toString() || tec.id?.toString(),
        name: tec.user?.get_full_name || tec.user?.username || tec.nombre || 'Sin nombre',
        email: tec.user?.email || tec.email || 'Sin email',
        phone: tec.telefono || tec.phone || 'Sin teléfono',
        status: tec.disponible ? 'available' : 'busy',
        activeOrders: tec.ordenes_activas || 0,
        specialties: tec.especialidades || [],
        avatar: (tec.user?.first_name?.[0] || '') + (tec.user?.last_name?.[0] || '') || 'T'
      }));
      
      setTechnicians(tecnicosTransformados);
      console.log('✅ Técnicos cargados:', tecnicosTransformados.length);
    } catch (err) {
      console.error("❌ Error fetching technicians:", err);
      setTechnicians([]);
      setError("No se pudo cargar la información de técnicos.");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (technician: Technician) => {
    setSelectedTechnician(technician);
    setShowEditForm(true);
  };

  const handleDelete = (technician: Technician) => {
    setSelectedTechnician(technician);
    setShowDeleteDialog(true);
  };

  const confirmDelete = async () => {
    if (!selectedTechnician) return;
    
    try {
      console.log('Eliminando técnico:', selectedTechnician.id);
      
      // TODO: Implementar eliminación en el backend
      // await tecnicosService.delete(parseInt(selectedTechnician.id));
      
      // Simular eliminación
      await new Promise(resolve => setTimeout(resolve, 500));
      
      alert('Técnico eliminado exitosamente');
      setShowDeleteDialog(false);
      setSelectedTechnician(null);
      
      // Recargar datos
      fetchTechnicians();
    } catch (err) {
      console.error('Error eliminando técnico:', err);
      alert('Error al eliminar el técnico');
    }
  };

  const handleSuccess = () => {
    fetchTechnicians();
    setSelectedTechnician(null);
  };

  const getStatusBadge = (status: string, activeOrders: number) => {
    switch (status) {
      case 'available': 
        return <Badge variant="completed">Disponible</Badge>;
      case 'busy': 
        return (
          <div className="flex items-center gap-2">
            <Badge variant="pending">Ocupado</Badge>
            <Badge variant="secondary">{activeOrders} OT activa{activeOrders !== 1 ? 's' : ''}</Badge>
          </div>
        );
      case 'offline': 
        return <Badge variant="secondary">Fuera de Servicio</Badge>;
      default: 
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getFilteredTechnicians = () => {
    switch (activeTab) {
      case 'available':
        return technicians.filter(t => t.status === 'available');
      case 'busy':
        return technicians.filter(t => t.status === 'busy');
      case 'offline':
        return technicians.filter(t => t.status === 'offline');
      default:
        return technicians;
    }
  };

  const tabs = [
    { id: 'all', label: `Todos (${mockStats.total})` },
    { id: 'available', label: `Disponibles (${mockStats.available})` },
    { id: 'busy', label: `Ocupados (${mockStats.busy})` },
    { id: 'offline', label: `Fuera de Servicio (${mockStats.offline})` }
  ];

  // Handlers para acciones
  const handleViewProfile = (technician: Technician) => {
    setSelectedTechnician(technician);
    console.log('Ver perfil de:', technician.name);
  };

  if (loading) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
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
        title="Técnicos" 
        subtitle="Gestión de personal técnico y especialistas"
      >
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Técnico
        </Button>
      </PageHeader>

      {/* Tarjetas de resumen */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Técnicos</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.total}</div>
            <p className="text-xs text-muted-foreground">
              Personal registrado
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Disponibles</CardTitle>
            <UserCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{mockStats.available}</div>
            <p className="text-xs text-muted-foreground">
              Listos para asignar
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ocupados</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{mockStats.busy}</div>
            <p className="text-xs text-muted-foreground">
              En trabajo activo
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">OT Activas</CardTitle>
            <Wrench className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.total}</div>
            <p className="text-xs text-muted-foreground">
              Órdenes en progreso
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Pestañas de filtro */}
      <Card>
        <CardContent className="p-6">
          <div className="flex space-x-1 bg-muted p-1 rounded-lg w-fit">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === tab.id
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Lista de técnicos */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {getFilteredTechnicians().map((technician) => (
          <Card key={technician.id}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground font-medium">
                    {technician.avatar}
                  </div>
                  <div>
                    <h3 className="font-semibold">{technician.name}</h3>
                    {getStatusBadge(technician.status, technician.activeOrders)}
                  </div>
                </div>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Mail className="h-4 w-4" />
                  {technician.email}
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Phone className="h-4 w-4" />
                  {technician.phone}
                </div>
              </div>

              <div className="mb-4">
                <h4 className="text-sm font-medium mb-2">Especialidades</h4>
                <div className="flex flex-wrap gap-1">
                  {technician.specialties.map((specialty, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {specialty}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="flex-1"
                  onClick={() => handleViewProfile(technician)}
                >
                  <Eye className="h-4 w-4 mr-2" />
                  Ver Perfil
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="flex-1"
                  onClick={() => handleEdit(technician)}
                >
                  <Edit className="h-4 w-4 mr-2" />
                  Editar
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Formulario de creación de técnico */}
      <CreateTecnicoForm
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={() => {
          fetchTechnicians();
        }}
      />

      {/* Formulario de edición de técnico */}
      {selectedTechnician && (
        <CreateTecnicoForm
          isOpen={showEditForm}
          onClose={() => {
            setShowEditForm(false);
            setSelectedTechnician(null);
          }}
          onSuccess={() => {
            fetchTechnicians();
            setShowEditForm(false);
            setSelectedTechnician(null);
          }}
          tecnicoData={selectedTechnician}
        />
      )}

      {/* Diálogo de confirmación de eliminación */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Estás seguro?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará permanentemente el técnico "{selectedTechnician?.name}".
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

export default TecnicosView;

