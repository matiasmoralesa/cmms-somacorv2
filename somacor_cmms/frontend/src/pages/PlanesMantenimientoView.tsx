import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Calendar, 
  Clock, 
  AlertTriangle, 
  Wrench, 
  User,
  ToggleLeft,
  ToggleRight,
  Edit,
  Trash2,
  Eye
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import CreateMaintenancePlanForm from '@/components/forms/CreateMaintenancePlanForm';
import { planesMantenimientoService } from '@/services/planesMantenimientoService';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';

interface MaintenancePlan {
  id: string;
  name: string;
  equipment: string;
  frequency: string;
  nextDate: string;
  active: boolean;
}

interface UpcomingMaintenance {
  id: string;
  title: string;
  equipment: string;
  date: string;
  assignedTo: string;
  estimatedTime: string;
  tasks: number;
  status: 'overdue' | 'upcoming';
}

const PlanesMantenimientoView: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingPlan, setEditingPlan] = useState<MaintenancePlan | undefined>(undefined);
  const [deleteConfirm, setDeleteConfirm] = useState<{isOpen: boolean, plan: MaintenancePlan | null}>({isOpen: false, plan: null});

  // Datos de ejemplo para el diseño
  const mockStats = {
    planesActivos: 4,
    estaSemana: 0,
    vencidos: 4,
    horasTotales: 11
  };

  const mockUpcomingMaintenance: UpcomingMaintenance[] = [
    {
      id: "1",
      title: "Mantenimiento Mensual Bomba",
      equipment: "Bomba Centrífuga B-205",
      date: "31-10-2024",
      assignedTo: "María García",
      estimatedTime: "2h estimadas",
      tasks: 5,
      status: "overdue"
    },
    {
      id: "2",
      title: "Mantenimiento Trimestral Compresor",
      equipment: "Compresor de Aire Principal",
      date: "14-12-2024",
      assignedTo: "Juan Pérez",
      estimatedTime: "3h estimadas",
      tasks: 8,
      status: "upcoming"
    },
    {
      id: "3",
      title: "Mantenimiento Semestral Motor",
      equipment: "Motor Eléctrico C-310",
      date: "19-02-2025",
      assignedTo: "Carlos López",
      estimatedTime: "4h estimadas",
      tasks: 12,
      status: "upcoming"
    },
    {
      id: "4",
      title: "Mantenimiento Anual Válvula",
      equipment: "Válvula de Control D-115",
      date: "09-09-2025",
      assignedTo: "Ana Martínez",
      estimatedTime: "2h estimadas",
      tasks: 6,
      status: "upcoming"
    }
  ];

  const mockMaintenancePlans: MaintenancePlan[] = [
    {
      id: "1",
      name: "Mantenimiento Trimestral Compresor",
      equipment: "Compresor de Aire Principal",
      frequency: "Trimestral",
      nextDate: "14-12-2024",
      active: true
    },
    {
      id: "2",
      name: "Mantenimiento Mensual Bomba",
      equipment: "Bomba Centrífuga B-205",
      frequency: "Mensual",
      nextDate: "31-10-2024",
      active: true
    },
    {
      id: "3",
      name: "Mantenimiento Semestral Motor",
      equipment: "Motor Eléctrico C-310",
      frequency: "Semestral",
      nextDate: "19-02-2025",
      active: true
    },
    {
      id: "4",
      name: "Mantenimiento Anual Válvula",
      equipment: "Válvula de Control D-115",
      frequency: "Anual",
      nextDate: "09-09-2025",
      active: true
    }
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // TODO: Cargar datos reales del backend
      // const data = await planesMantenimientoService.getAll();
      // setPlanes(data.results);
      
      console.log('Datos cargados correctamente');
    } catch (err) {
      console.error("Error fetching maintenance data:", err);
      setError("No se pudo cargar la información de mantenimiento preventivo.");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (plan: MaintenancePlan) => {
    setEditingPlan(plan);
    setShowCreateForm(true);
  };

  const handleDelete = (plan: MaintenancePlan) => {
    setDeleteConfirm({isOpen: true, plan});
  };

  const confirmDelete = async () => {
    if (!deleteConfirm.plan || !deleteConfirm.plan.id) return;
    
    try {
      console.log('Eliminando plan:', deleteConfirm.plan.id);
      
      // TODO: Implementar eliminación en el backend
      // await planesMantenimientoService.delete(parseInt(deleteConfirm.plan.id));
      
      // Simular eliminación
      await new Promise(resolve => setTimeout(resolve, 500));
      
      alert('Plan de mantenimiento eliminado exitosamente');
      setDeleteConfirm({isOpen: false, plan: null});
      
      // Recargar datos
      fetchData();
    } catch (err) {
      console.error('Error eliminando plan:', err);
      alert('Error al eliminar el plan de mantenimiento');
    }
  };

  const cancelDelete = () => {
    setDeleteConfirm({isOpen: false, plan: null});
  };

  const handleToggleActivo = async (plan: MaintenancePlan) => {
    if (!plan.id) return;
    
    try {
      console.log('Toggle activo para plan:', plan.id, 'Nuevo estado:', !plan.active);
      
      // TODO: Implementar toggle en el backend
      // await planesMantenimientoService.toggleActivo(parseInt(plan.id), !plan.active);
      
      alert(`Plan ${!plan.active ? 'activado' : 'desactivado'} exitosamente`);
      
      // Recargar datos
      fetchData();
    } catch (err) {
      console.error('Error toggling plan:', err);
      alert('Error al cambiar el estado del plan');
    }
  };

  const handleSuccess = () => {
    fetchData();
    setEditingPlan(undefined);
  };

  const getStatusBadge = (status: string) => {
    if (status === 'overdue') {
      return <Badge variant="urgent">Vencido hace 343 días</Badge>;
    }
    return <Badge variant="secondary">Programado</Badge>;
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
        title="Mantenimiento Preventivo" 
        subtitle="Gestión de planes y programación de mantenimientos preventivos"
      >
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Plan
        </Button>
      </PageHeader>

      {/* Tarjetas de resumen */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Planes Activos</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.planesActivos}</div>
            <p className="text-xs text-muted-foreground">
              De {mockStats.planesActivos} totales
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Esta Semana</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.estaSemana}</div>
            <p className="text-xs text-muted-foreground">
              Mantenimientos programados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vencidos</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{mockStats.vencidos}</div>
            <p className="text-xs text-muted-foreground">
              Requieren atención
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Horas Totales</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.horasTotales}h</div>
            <p className="text-xs text-muted-foreground">
              Estimadas por ciclo
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Próximos mantenimientos */}
      <Card>
        <CardHeader>
          <CardTitle>Próximos Mantenimientos</CardTitle>
          <CardDescription>Calendario de mantenimientos programados</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockUpcomingMaintenance.map((maintenance) => (
              <div key={maintenance.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">{maintenance.title}</h3>
                    {getStatusBadge(maintenance.status)}
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{maintenance.equipment}</p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      {maintenance.date}
                    </div>
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-muted-foreground" />
                      {maintenance.assignedTo}
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      {maintenance.estimatedTime}
                    </div>
                    <div className="flex items-center gap-2">
                      <Wrench className="h-4 w-4 text-muted-foreground" />
                      {maintenance.tasks} tareas
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Planes de mantenimiento */}
      <Card>
        <CardHeader>
          <CardTitle>Planes de Mantenimiento</CardTitle>
          <CardDescription>Todos los planes configurados</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Plan</TableHead>
                <TableHead>Frecuencia</TableHead>
                <TableHead>Próximo</TableHead>
                <TableHead>Activo</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockMaintenancePlans.map((plan) => (
                <TableRow key={plan.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{plan.name}</div>
                      <div className="text-sm text-muted-foreground">{plan.equipment}</div>
                    </div>
                  </TableCell>
                  <TableCell>{plan.frequency}</TableCell>
                  <TableCell>{plan.nextDate}</TableCell>
                  <TableCell>
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => handleToggleActivo(plan)}
                      title={plan.active ? 'Desactivar plan' : 'Activar plan'}
                    >
                      {plan.active ? (
                        <ToggleRight className="h-4 w-4 text-primary" />
                      ) : (
                        <ToggleLeft className="h-4 w-4 text-muted-foreground" />
                      )}
                    </Button>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm" onClick={() => handleEdit(plan)}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleDelete(plan)}>
                        <Trash2 className="h-4 w-4 text-red-600" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Formulario de creación/edición de plan de mantenimiento */}
      <CreateMaintenancePlanForm
        isOpen={showCreateForm}
        onClose={() => {
          setShowCreateForm(false);
          setEditingPlan(undefined);
        }}
        onSuccess={handleSuccess}
        maintenancePlanData={editingPlan}
      />

      {/* Diálogo de confirmación de eliminación */}
      <AlertDialog open={deleteConfirm.isOpen} onOpenChange={setDeleteConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Eliminar plan de mantenimiento?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará permanentemente el plan{' '}
              <strong>{deleteConfirm.plan?.name}</strong>.
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
};

export default PlanesMantenimientoView;


