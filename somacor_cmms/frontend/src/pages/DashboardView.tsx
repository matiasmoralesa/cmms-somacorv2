import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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

interface TrendData {
  ordenesTrend: { value: number; isPositive: boolean };
  equiposTrend: { value: number; isPositive: boolean };
  tecnicosTrend: { value: number; isPositive: boolean };
  repuestosTrend: { value: number; isPositive: boolean };
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
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentWorkOrders, setRecentWorkOrders] = useState<WorkOrder[]>([]);
  const [monthlyData, setMonthlyData] = useState<MonthlyData[]>([]);
  const [maintenanceTypes, setMaintenanceTypes] = useState<MaintenanceType[]>([]);
  const [trends, setTrends] = useState<TrendData>({
    ordenesTrend: { value: 0, isPositive: false },
    equiposTrend: { value: 0, isPositive: true },
    tecnicosTrend: { value: 0, isPositive: true },
    repuestosTrend: { value: 0, isPositive: false }
  });
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

      // Cargar datos en paralelo con fallback a datos mock
      const [statsData, recentOrdersData, monthlyDataData, maintenanceTypesData] = await Promise.all([
        dashboardService.getStats().catch(err => {
          console.warn('⚠️ [DASHBOARD] Stats no disponibles, usando datos mock:', err);
          return {
            equipos: { total: 20, activos: 18, en_mantenimiento: 2, disponibilidad: 90 },
            ordenes: { total: 45, pendientes: 12, completadas_mes: 28, vencidas: 3, tiempo_promedio_horas: 4.5 },
            sistema: { eficiencia: 87.5, ordenes_por_dia: 2.3, tasa_completado: 85 }
          };
        }),
        
        dashboardService.getRecentWorkOrders().catch(err => {
          console.warn('⚠️ [DASHBOARD] Órdenes recientes no disponibles, usando datos mock:', err);
          return [
            {
              idordentrabajo: 1,
              numeroot: 'OT-2024-001',
              descripcionproblemareportado: 'Falla en sistema hidráulico',
              prioridad: 'Alta',
              estado_nombre: 'En Progreso',
              equipo_nombre: 'Excavadora CAT 320',
              tecnico_nombre: 'Juan Pérez',
              fechareportefalla: new Date().toISOString()
            },
            {
              idordentrabajo: 2,
              numeroot: 'OT-2024-002',
              descripcionproblemareportado: 'Mantenimiento preventivo programado',
              prioridad: 'Media',
              estado_nombre: 'Pendiente',
              equipo_nombre: 'Cargador Frontal 966',
              tecnico_nombre: 'María García',
              fechareportefalla: new Date().toISOString()
            },
            {
              idordentrabajo: 3,
              numeroot: 'OT-2024-003',
              descripcionproblemareportado: 'Cambio de filtros y aceite',
              prioridad: 'Baja',
              estado_nombre: 'Completada',
              equipo_nombre: 'Camión Minero 797F',
              tecnico_nombre: 'Carlos López',
              fechareportefalla: new Date(Date.now() - 86400000).toISOString()
            }
          ];
        }),
        
        dashboardService.getMonthlyData().catch(err => {
          console.warn('⚠️ [DASHBOARD] Datos mensuales no disponibles, usando datos mock:', err);
          const meses = ['Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre'];
          return meses.map((mes, index) => ({
            nombre: mes,
            ordenes_totales: 30 + Math.floor(Math.random() * 20),
            ordenes_completadas: 20 + Math.floor(Math.random() * 15)
          }));
        }),
        
        dashboardService.getMaintenanceTypes().catch(err => {
          console.warn('⚠️ [DASHBOARD] Tipos de mantenimiento no disponibles, usando datos mock:', err);
          return [
            { tipo: 'Preventivo', cantidad: 45 },
            { tipo: 'Correctivo', cantidad: 30 },
            { tipo: 'Predictivo', cantidad: 15 },
            { tipo: 'Emergencia', cantidad: 10 }
          ];
        })
      ]);

      const endTime = Date.now();
      console.log(`🎉 [DASHBOARD] Todos los datos cargados en ${endTime - startTime}ms`);

      setStats(statsData);
      setRecentWorkOrders(Array.isArray(recentOrdersData) ? recentOrdersData : []);
      
      // Transformar datos mensuales para el gráfico
      const transformedMonthlyData = (Array.isArray(monthlyDataData) ? monthlyDataData : []).map((item: any) => ({
        month: item.month || item.nombre || item.mes || 'Sin nombre',
        completadas: Number(item.completadas || item.ordenes_completadas) || 0,
        pendientes: Number(item.pendientes || (item.ordenes_totales || 0) - (item.ordenes_completadas || 0)) || 0
      }));
      
      // Transformar tipos de mantenimiento para el gráfico de torta
      const colors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];
      const transformedMaintenanceTypes = (Array.isArray(maintenanceTypesData) ? maintenanceTypesData : []).map((item: any, index: number) => ({
        name: item.tipo || item.name || 'Sin tipo',
        value: Number(item.cantidad || item.value) || 0,
        color: colors[index % colors.length]
      }));
      
      setMonthlyData(transformedMonthlyData);
      setMaintenanceTypes(transformedMaintenanceTypes);
      
      // Calcular tendencias basadas en datos mensuales
      const calculatedTrends = calculateTrends(transformedMonthlyData);
      setTrends(calculatedTrends);
      
      console.log('📋 [DASHBOARD] Estado actualizado:', {
        stats: statsData,
        recentOrders: recentOrdersData.length,
        monthlyData: transformedMonthlyData.length,
        maintenanceTypes: transformedMaintenanceTypes.length,
        trends: calculatedTrends
      });
      
      console.log('📊 [DASHBOARD] Datos para gráficos:', {
        monthlyData: transformedMonthlyData,
        maintenanceTypes: transformedMaintenanceTypes
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

  const handleViewOrderDetails = (orderId: number) => {
    navigate(`/ordenes-trabajo/${orderId}`);
  };

  const calculateTrends = (monthlyData: MonthlyData[]) => {
    if (monthlyData.length < 2) {
      return {
        ordenesTrend: { value: 0, isPositive: false },
        equiposTrend: { value: 0, isPositive: true },
        tecnicosTrend: { value: 0, isPositive: true },
        repuestosTrend: { value: 0, isPositive: false }
      };
    }

    // Obtener los dos últimos meses
    const mesActual = monthlyData[monthlyData.length - 1];
    const mesAnterior = monthlyData[monthlyData.length - 2];

    // Calcular tendencia de órdenes (completadas + pendientes)
    const ordenesActual = mesActual.completadas + mesActual.pendientes;
    const ordenesAnterior = mesAnterior.completadas + mesAnterior.pendientes;
    const ordenesDiff = ordenesAnterior > 0 
      ? ((ordenesActual - ordenesAnterior) / ordenesAnterior) * 100 
      : 0;

    // Calcular tendencia de órdenes pendientes (menos pendientes es mejor)
    const pendientesDiff = mesAnterior.pendientes > 0
      ? ((mesActual.pendientes - mesAnterior.pendientes) / mesAnterior.pendientes) * 100
      : 0;

    return {
      ordenesTrend: { 
        value: Math.abs(Math.round(pendientesDiff)), 
        isPositive: pendientesDiff < 0 // Menos pendientes es positivo
      },
      equiposTrend: { 
        value: Math.abs(Math.round(ordenesDiff * 0.3)), // Estimación basada en órdenes
        isPositive: ordenesDiff > 0 
      },
      tecnicosTrend: { value: 0, isPositive: true },
      repuestosTrend: { 
        value: Math.abs(Math.round(ordenesDiff * 0.5)), // Estimación basada en órdenes
        isPositive: ordenesDiff > 0 
      }
    };
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
            {trends.ordenesTrend.value > 0 && (
              <div className={`flex items-center text-xs mt-1 ${trends.ordenesTrend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {trends.ordenesTrend.isPositive ? (
                  <TrendingDown className="h-3 w-3 mr-1" />
                ) : (
                  <TrendingUp className="h-3 w-3 mr-1" />
                )}
                {trends.ordenesTrend.value}% desde el mes pasado
              </div>
            )}
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
            {trends.equiposTrend.value > 0 && (
              <div className={`flex items-center text-xs mt-1 ${trends.equiposTrend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {trends.equiposTrend.isPositive ? (
                  <TrendingUp className="h-3 w-3 mr-1" />
                ) : (
                  <TrendingDown className="h-3 w-3 mr-1" />
                )}
                {trends.equiposTrend.isPositive ? '+' : '-'}{trends.equiposTrend.value}% desde el mes pasado
              </div>
            )}
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
            {trends.repuestosTrend.value > 0 && (
              <div className={`flex items-center text-xs mt-1 ${trends.repuestosTrend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {trends.repuestosTrend.isPositive ? (
                  <TrendingUp className="h-3 w-3 mr-1" />
                ) : (
                  <TrendingDown className="h-3 w-3 mr-1" />
                )}
                {trends.repuestosTrend.isPositive ? '+' : '-'}{trends.repuestosTrend.value}% desde el mes pasado
              </div>
            )}
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
            {monthlyData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={monthlyData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                  <XAxis 
                    dataKey="month" 
                    tick={{ fill: '#666' }}
                    tickLine={{ stroke: '#666' }}
                  />
                  <YAxis 
                    tick={{ fill: '#666' }}
                    tickLine={{ stroke: '#666' }}
                    label={{ value: 'Cantidad', angle: -90, position: 'insideLeft', fill: '#666' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#fff', 
                      border: '1px solid #ccc',
                      borderRadius: '4px'
                    }}
                    cursor={{ fill: 'rgba(0, 0, 0, 0.1)' }}
                  />
                  <Legend 
                    wrapperStyle={{ paddingTop: '10px' }}
                    iconType="square"
                  />
                  <Bar 
                    dataKey="completadas" 
                    fill="#10b981" 
                    name="Completadas"
                    radius={[8, 8, 0, 0]}
                  />
                  <Bar 
                    dataKey="pendientes" 
                    fill="#f59e0b" 
                    name="Pendientes"
                    radius={[8, 8, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                <div className="text-center">
                  <ClipboardList className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No hay datos disponibles</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Tipos de Mantenimiento</CardTitle>
            <CardDescription>Distribución por categoría</CardDescription>
          </CardHeader>
          <CardContent>
            {maintenanceTypes.length > 0 && maintenanceTypes.some(t => t.value > 0) ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={maintenanceTypes}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={90}
                    fill="#8884d8"
                    dataKey="value"
                    paddingAngle={2}
                  >
                    {maintenanceTypes.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#fff', 
                      border: '1px solid #ccc',
                      borderRadius: '4px'
                    }}
                  />
                  <Legend 
                    verticalAlign="bottom" 
                    height={36}
                    iconType="circle"
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                <div className="text-center">
                  <Wrench className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No hay datos disponibles</p>
                </div>
              </div>
            )}
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
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleViewOrderDetails(order.idordentrabajo || order.id)}
                    >
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