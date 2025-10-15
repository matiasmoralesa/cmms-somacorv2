import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { 
  ClipboardList, 
  Wrench, 
  Users, 
  Package,
  Plus,
  Clock,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Eye
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { dashboardService } from '@/services/apiService';
import CreateWorkOrderForm from '@/components/forms/CreateWorkOrderForm';
import { useRealtimeUpdates } from '@/hooks/useRealtimeUpdates';
import ConnectionStatus from '@/components/ConnectionStatus';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface DashboardStats {
  equipos: {
    total: number;
    activos: number;
    en_mantenimiento: number;
    disponibilidad: number;
  };
  ordenes: {
    total: number;
    pendientes: number;
    completadas_mes: number;
    vencidas: number;
    tiempo_promedio_horas: number;
  };
  sistema: {
    eficiencia: number;
    ordenes_por_dia: number;
    tasa_completado: number;
  };
}

interface WorkOrder {
  id: number;
  title: string;
  equipment: string;
  technician: string;
  priority: string;
  status: string;
  type: string;
}

interface MonthlyData {
  month: string;
  completadas: number;
  pendientes: number;
}

interface MaintenanceType {
  name: string;
  value: number;
  color: string;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

export default function DashboardView() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentWorkOrders, setRecentWorkOrders] = useState<WorkOrder[]>([]);
  const [monthlyData, setMonthlyData] = useState<MonthlyData[]>([]);
  const [maintenanceTypes, setMaintenanceTypes] = useState<MaintenanceType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  
  // Real-time updates
  const { realtimeData, connectionStatus, subscribeToUpdates } = useRealtimeUpdates({
    onDataUpdate: (dataType, data) => {
      console.log('Dashboard data updated:', dataType, data);
      // Refresh dashboard data when real-time updates are received
      if (dataType === 'dashboard_update') {
        loadDashboardData();
      }
    }
  });

  // =================================================================================
  // EFECTOS
  // =================================================================================

  useEffect(() => {
    loadDashboardData();
    // Subscribe to dashboard updates
    subscribeToUpdates('dashboard');
  }, []);

  // =================================================================================
  // FUNCIONES
  // =================================================================================

  const loadDashboardData = async () => {
    console.log('🚀 [DASHBOARD] Iniciando carga de datos del dashboard');
    
    try {
      setLoading(true);
      setError(null);

      console.log('📊 [DASHBOARD] Cargando estadísticas...');
      const startTime = Date.now();

      // Cargar datos en paralelo
      const [statsData, recentOrdersData, monthlyDataData, maintenanceTypesData] = await Promise.all([
        dashboardService.getStats().then(data => {
          console.log('✅ [DASHBOARD] Stats cargadas:', data);
          return data;
        }).catch(err => {
          console.error('❌ [DASHBOARD] Error cargando stats:', err);
          throw err;
        }),
        
        dashboardService.getRecentWorkOrders().then(data => {
          console.log('✅ [DASHBOARD] Órdenes recientes cargadas:', data);
          return data;
        }).catch(err => {
          console.error('❌ [DASHBOARD] Error cargando órdenes recientes:', err);
          throw err;
        }),
        
        dashboardService.getMonthlyData().then(data => {
          console.log('✅ [DASHBOARD] Datos mensuales cargados:', data);
          return data;
        }).catch(err => {
          console.error('❌ [DASHBOARD] Error cargando datos mensuales:', err);
          throw err;
        }),
        
        dashboardService.getMaintenanceTypes().then(data => {
          console.log('✅ [DASHBOARD] Tipos de mantenimiento cargados:', data);
          return data;
        }).catch(err => {
          console.error('❌ [DASHBOARD] Error cargando tipos de mantenimiento:', err);
          throw err;
        })
      ]);

      const endTime = Date.now();
      console.log(`🎉 [DASHBOARD] Todos los datos cargados en ${endTime - startTime}ms`);

      setStats(statsData);
      setRecentWorkOrders(recentOrdersData);
      
      // Transformar datos mensuales para el gráfico
      const transformedMonthlyData = monthlyDataData.map((item: any) => ({
        month: item.nombre || item.mes,
        completadas: item.ordenes_completadas || 0,
        pendientes: (item.ordenes_totales || 0) - (item.ordenes_completadas || 0)
      }));
      
      // Transformar tipos de mantenimiento para el gráfico de torta
      const colors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];
      const transformedMaintenanceTypes = maintenanceTypesData.map((item: any, index: number) => ({
        name: item.tipo || item.name,
        value: item.cantidad || item.value || 0,
        color: colors[index % colors.length]
      }));
      
      setMonthlyData(transformedMonthlyData);
      setMaintenanceTypes(transformedMaintenanceTypes);
      
      console.log('📋 [DASHBOARD] Estado actualizado:', {
        stats: statsData,
        recentOrders: recentOrdersData.length,
        monthlyData: monthlyDataData.length,
        maintenanceTypes: maintenanceTypesData.length
      });
      
    } catch (err) {
      console.error('💥 [DASHBOARD] Error loading dashboard data:', err);
      setError('Error al cargar los datos del dashboard');
    } finally {
      setLoading(false);
      console.log('🏁 [DASHBOARD] Carga completada');
    }
  };

  const getPriorityColor = (priority: string) => {
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
    switch (status.toLowerCase()) {
      case 'completada':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100';
      case 'en progreso':
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
    switch (priority.toLowerCase()) {
      case 'crítica':
      case 'urgente':
        return <AlertTriangle className="h-4 w-4" />;
      case 'alta':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  // =================================================================================
  // RENDER
  // =================================================================================

  if (loading) {
    return (
      <PageLayout>
        <PageHeader
          title="Dashboard"
          description="Cargando datos del sistema..."
        />
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Cargando dashboard...</p>
          </div>
        </div>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout>
        <PageHeader
          title="Dashboard"
          description="Error al cargar los datos"
        />
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-4" />
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={loadDashboardData} variant="outline">
              Reintentar
            </Button>
          </div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader
        title="Dashboard"
        description="Resumen general del sistema de mantenimiento"
        action={
          <div className="flex items-center gap-3">
            <ConnectionStatus status={connectionStatus} />
            <Button 
              className="bg-primary hover:bg-primary/90"
              onClick={() => setShowCreateForm(true)}
            >
              <Plus className="h-4 w-4 mr-2" />
              Nueva Orden de Trabajo
            </Button>
          </div>
        }
      />

      {/* Estadísticas principales */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Órdenes Activas</CardTitle>
            <ClipboardList className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.ordenes.pendientes || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.ordenes.vencidas || 0} urgentes
            </p>
            <div className="flex items-center text-xs text-muted-foreground mt-1">
              <TrendingDown className="h-3 w-3 mr-1" />
              12% desde el mes pasado
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Equipos Totales</CardTitle>
            <Wrench className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.equipos.total || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.equipos.activos || 0} operativos
            </p>
            <div className="flex items-center text-xs text-muted-foreground mt-1">
              <TrendingUp className="h-3 w-3 mr-1" />
              +5% desde el mes pasado
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Técnicos Disponibles</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">
              De 0 totales
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Repuestos Críticos</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">
              Requieren reorden
            </p>
            <div className="flex items-center text-xs text-muted-foreground mt-1">
              <TrendingUp className="h-3 w-3 mr-1" />
              +15% desde el mes pasado
            </div>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Gráficos */}
      <ContentGrid>
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle>Órdenes de Trabajo</CardTitle>
            <CardDescription>Completadas vs Pendientes (últimos 6 meses)</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="completadas" fill="oklch(0.6 0.15 160)" name="Completadas" />
                <Bar dataKey="pendientes" fill="oklch(0.65 0.2 40)" name="Pendientes" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Tipos de Mantenimiento</CardTitle>
            <CardDescription>Distribución por categoría</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={maintenanceTypes}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {maintenanceTypes.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </ContentGrid>

      {/* Órdenes de trabajo recientes */}
      <Card>
        <CardHeader>
          <CardTitle>Órdenes de Trabajo Recientes</CardTitle>
          <CardDescription>Últimas actividades del sistema</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentWorkOrders.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No hay órdenes de trabajo recientes
              </div>
            ) : (
              recentWorkOrders.map((order, index) => (
                <div key={order.idordentrabajo || order.id || index} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-medium">{order.numeroot || `WO-${(order.idordentrabajo || order.id || index + 1).toString().padStart(3, '0')}`}: {order.descripcionproblemareportado || order.title || 'Sin descripción'}</h4>
                      <Badge variant={getPriorityColor(order.prioridad || order.priority)} className="text-xs">
                        {getPriorityIcon(order.prioridad || order.priority)}
                        <span className="ml-1">{order.prioridad || order.priority}</span>
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <span className="font-medium">{order.equipo_nombre || order.equipment}</span> • Asignado a: {order.tecnico_nombre || order.technician}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(order.estado_nombre || order.status)}`}>
                      {order.estado_nombre || order.status}
                    </span>
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4 mr-1" />
                      Ver Detalles
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* Formulario de creación de orden de trabajo */}
      <CreateWorkOrderForm
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={() => {
          loadDashboardData(); // Recargar datos después de crear
        }}
      />
    </PageLayout>
  );
}