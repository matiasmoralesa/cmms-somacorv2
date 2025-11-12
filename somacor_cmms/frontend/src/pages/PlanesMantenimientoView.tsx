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
import { ordenesTrabajoService, equiposService } from '@/services/apiService';
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
  
  // Estados para datos reales
  const [stats, setStats] = useState({
    planesActivos: 0,
    estaSemana: 0,
    vencidos: 0,
    horasTotales: 0
  });
  const [upcomingMaintenance, setUpcomingMaintenance] = useState<UpcomingMaintenance[]>([]);
  const [maintenancePlans, setMaintenancePlans] = useState<MaintenancePlan[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Cargar órdenes de trabajo de tipo preventivo
      const ordenesResponse = await ordenesTrabajoService.getAll({ limit: 100 });
      const ordenes = ordenesResponse.results || [];
      
      // Filtrar órdenes preventivas
      const ordenesPreventivas = ordenes.filter((orden: any) => 
        orden.tipo_mantenimiento_nombre?.toLowerCase().includes('preventivo')
      );
      
      // Calcular estadísticas
      const ahora = new Date();
      const estaSemana = new Date(ahora.getTime() + 7 * 24 * 60 * 60 * 1000);
      
      const ordenesEstaSemana = ordenesPreventivas.filter((orden: any) => {
        if (!orden.fechaejecucion) return false;
        const fechaEjecucion = new Date(orden.fechaejecucion);
        return fechaEjecucion >= ahora && fechaEjecucion <= estaSemana;
      });
      
      const ordenesVencidas = ordenesPreventivas.filter((orden: any) => {
        if (!orden.fechaejecucion) return false;
        const fechaEjecucion = new Date(orden.fechaejecucion);
        return fechaEjecucion < ahora && orden.estado_nombre !== 'Completada';
      });
      
      const horasTotales = ordenesPreventivas.reduce((total: number, orden: any) => {
        return total + (orden.tiempototalminutos || 0);
      }, 0) / 60;
      
      setStats({
        planesActivos: ordenesPreventivas.length,
        estaSemana: ordenesEstaSemana.length,
        vencidos: ordenesVencidas.length,
        horasTotales: Math.round(horasTotales)
      });
      
      // Transformar órdenes a próximos mantenimientos
      const proximosMantenimientos: UpcomingMaintenance[] = ordenesPreventivas
        .slice(0, 10)
        .map((orden: any) => {
          const fechaEjecucion = orden.fechaejecucion ? new Date(orden.fechaejecucion) : new Date();
          const isOverdue = fechaEjecucion < ahora && orden.estado_nombre !== 'Completada';
          
          return {
            id: orden.idordentrabajo?.toString() || '',
            title: orden.descripcionproblemareportado || 'Mantenimiento Preventivo',
            equipment: orden.equipo_nombre || 'Sin equipo',
            date: fechaEjecucion.toLocaleDateString('es-CL'),
            assignedTo: orden.tecnico_nombre || 'Sin asignar',
            estimatedTime: `${Math.round((orden.tiempototalminutos || 120) / 60)}h estimadas`,
            tasks: 5,
            status: isOverdue ? 'overdue' as const : 'upcoming' as const
          };
        });
      
      setUpcomingMaintenance(proximosMantenimientos);
      
      // Transformar órdenes a planes
      const planes: MaintenancePlan[] = ordenesPreventivas.map((orden: any) => ({
        id: orden.idordentrabajo?.toString() || '',
        name: orden.descripcionproblemareportado || 'Mantenimiento Preventivo',
        equipment: orden.equipo_nombre || 'Sin equipo',
        frequency: 'Mensual',
        nextDate: orden.fechaejecucion ? new Date(orden.fechaejecucion).toLocaleDateString('es-CL') : 'Sin fecha',
        active: orden.estado_nombre !== 'Cancelada'
      }));
      
      setMaintenancePlans(planes);
      
      console.log('✅ Datos cargados');
    } catch (err) {
      console.error("❌ Error:", err);
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
      console.log('🗑️ Eliminando orden de trabajo:', deleteConfirm.plan.id);
      
      // Eliminar la orden de trabajo (que representa el plan de mantenimiento)
      await ordenesTrabajoService.delete(parseInt(deleteConfirm.plan.id));
      
      console.log('✅ Orden eliminada exitosamente');
      setDeleteConfirm({isOpen: false, plan: null});
      
      // Recargar datos
      await fetchData();
    } catch (err: any) {
      console.error('❌ Error eliminando plan:', err);
      setError(err.response?.data?.message || 'Error al eliminar el plan de mantenimiento');
      setDeleteConfirm({isOpen: false, plan: null});
    }
  };

  const cancelDelete = () => {
    setDeleteConfirm({isOpen: false, plan: null});
  };

  const handleToggleActivo = async (plan: MaintenancePlan) => {
    if (!plan.id) return;
    
    try {
      console.log('🔄 Toggle activo para orden:', plan.id, 'Nuevo estado:', !plan.active);
      
      // Cambiar el estado de la orden de trabajo
      // Si está activa, la cancelamos; si está cancelada, la reactivamos
      const nuevoEstado = plan.active ? 'Cancelada' : 'Pendiente';
      
      await ordenesTrabajoService.update(parseInt(plan.id), {
        idestadoot: plan.active ? 4 : 1 // 4 = Cancelada, 1 = Pendiente (ajustar según tu BD)
      });
      
      console.log(`✅ Plan ${!plan.active ? 'activado' : 'desactivado'} exitosamente`);
      
      // Recargar datos
      await fetchData();
    } catch (err: any) {
      console.error('❌ Error toggling plan:', err);
      setError(err.response?.data?.message || 'Error al cambiar el estado del plan');
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

  const clearError = () => setError('');

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

      {/* Mensaje de error */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </div>
          <Button variant="ghost" size="sm" onClick={clearError}>
            ✕
          </Button>
        </div>
      )}

      {/* Tarjetas de resumen */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Planes Activos</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.planesActivos}</div>
            <p className="text-xs text-muted-foreground">
              De {stats.planesActivos} totales
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Esta Semana</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.estaSemana}</div>
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
            <div className="text-2xl font-bold text-destructive">{stats.vencidos}</div>
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
            <div className="text-2xl font-bold">{stats.horasTotales}h</div>
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
            {upcomingMaintenance.map((maintenance) => (
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
              {maintenancePlans.map((plan) => (
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


