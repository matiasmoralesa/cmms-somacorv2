import React, { useState, useEffect } from 'react';
import { X, Activity, Calendar, MapPin, Tag, Wrench, AlertCircle, CheckCircle, Clock, TrendingUp, Gauge, Download } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import axios from 'axios';

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

interface EquipmentDetails {
  equipo: any;
  metricas: {
    health_score: number;
    uptime: number;
    efficiency: number;
    availability: number;
    oee_score: number;
  };
  mantenimiento: {
    total_ordenes: number;
    ordenes_completadas: number;
    ordenes_pendientes: number;
    horas_mantenimiento: number;
    dias_desde_ultimo: number;
    ultimo_mantenimiento: string | null;
    proximo_mantenimiento: string | null;
  };
  fallas: {
    fallas_activas: number;
    fallas_30_dias: number;
  };
  estado: {
    nombre: string;
    activo: boolean;
  };
}

interface EquipmentDetailPanelProps {
  equipo: Equipo;
  onClose: () => void;
}

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

const EquipmentDetailPanel: React.FC<EquipmentDetailPanelProps> = ({ equipo, onClose }) => {
  const [details, setDetails] = useState<EquipmentDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get(`/v2/equipos/${equipo.id}/detalles/`);
        setDetails(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching equipment details:', err);
        setError('No se pudieron cargar los detalles del equipo');
        // Usar datos simulados como fallback
        setDetails({
          equipo: equipo,
          metricas: {
            health_score: getHealthScore(equipo.estado),
            uptime: equipo.estado === 'Operativo' ? 98.5 : equipo.estado === 'En Mantenimiento' ? 75 : 15,
            efficiency: equipo.estado === 'Operativo' ? 92 : equipo.estado === 'En Mantenimiento' ? 60 : 20,
            availability: equipo.estado === 'Operativo' ? 100 : 0,
            oee_score: equipo.estado === 'Operativo' ? 98 : equipo.estado === 'En Mantenimiento' ? 75 : 45,
          },
          mantenimiento: {
            total_ordenes: 0,
            ordenes_completadas: 0,
            ordenes_pendientes: equipo.estado === 'En Mantenimiento' ? 1 : 0,
            horas_mantenimiento: equipo.estado === 'Operativo' ? 2.5 : equipo.estado === 'En Mantenimiento' ? 5.2 : 12.8,
            dias_desde_ultimo: equipo.estado === 'Operativo' ? 12 : 8,
            ultimo_mantenimiento: equipo.ultimoMantenimiento,
            proximo_mantenimiento: '15-11-2024',
          },
          fallas: {
            fallas_activas: equipo.estado === 'Fuera de Servicio' ? 3 : equipo.estado === 'En Mantenimiento' ? 1 : 0,
            fallas_30_dias: 0,
          },
          estado: {
            nombre: equipo.estado,
            activo: equipo.activo,
          },
        });
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [equipo.id]);

  // Calcular métricas simuladas (fallback)
  const getHealthScore = (estado: string) => {
    switch (estado) {
      case 'Operativo': return 95;
      case 'En Mantenimiento': return 65;
      case 'Fuera de Servicio': return 25;
      default: return 50;
    }
  };

  const getStatusColor = (estado: string) => {
    switch (estado) {
      case 'Operativo': return 'text-green-600';
      case 'En Mantenimiento': return 'text-blue-600';
      case 'Fuera de Servicio': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusBgColor = (estado: string) => {
    switch (estado) {
      case 'Operativo': return 'bg-green-100';
      case 'En Mantenimiento': return 'bg-blue-100';
      case 'Fuera de Servicio': return 'bg-red-100';
      default: return 'bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-y-0 right-0 w-full md:w-[500px] bg-background border-l shadow-2xl z-50 overflow-y-auto animate-in slide-in-from-right duration-300">
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (!details) {
    return null;
  }

  const { metricas, mantenimiento, fallas, estado } = details;
  const healthScore = metricas.health_score;
  const uptime = metricas.uptime;
  const efficiency = metricas.efficiency;

  return (
    <div className="fixed inset-y-0 right-0 w-full md:w-[500px] bg-background border-l shadow-2xl z-50 overflow-y-auto animate-in slide-in-from-right duration-300">
      {/* Header */}
      <div className="sticky top-0 bg-background border-b p-6 flex justify-between items-start z-10">
        <div className="flex-1">
          <h2 className="text-2xl font-bold mb-1">{equipo.nombre}</h2>
          <p className="text-sm text-muted-foreground">{equipo.codigo}</p>
          {error && (
            <p className="text-xs text-yellow-600 mt-1">Usando datos simulados</p>
          )}
        </div>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-5 w-5" />
        </Button>
      </div>

      <div className="p-6 space-y-6">
        {/* Estado Principal con Gauge Visual */}
        <Card className={`${getStatusBgColor(equipo.estado)} border-2`}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-1">Estado Actual</p>
                <h3 className={`text-3xl font-bold ${getStatusColor(equipo.estado)}`}>
                  {equipo.estado}
                </h3>
              </div>
              <div className="relative w-24 h-24">
                {/* Gauge circular */}
                <svg className="w-24 h-24 transform -rotate-90">
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="none"
                    className="text-gray-200"
                  />
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${2 * Math.PI * 40}`}
                    strokeDashoffset={`${2 * Math.PI * 40 * (1 - healthScore / 100)}`}
                    className={getStatusColor(equipo.estado)}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className={`text-xl font-bold ${getStatusColor(equipo.estado)}`}>
                    {healthScore}%
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Activity className="h-4 w-4" />
              <span>Índice de Salud del Equipo</span>
            </div>
          </CardContent>
        </Card>

        {/* Información Básica */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Tag className="h-5 w-5" />
              Información del Equipo
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Marca</p>
                <p className="font-medium">{equipo.marca}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Modelo</p>
                <p className="font-medium">{equipo.modelo}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Categoría</p>
                <Badge variant="outline">{equipo.categoria}</Badge>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Patente</p>
                <p className="font-medium">{equipo.patente}</p>
              </div>
            </div>
            <div className="pt-2 border-t">
              <div className="flex items-center gap-2 text-sm">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Ubicación:</span>
                <span className="font-medium">{equipo.ubicacion}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Métricas de Rendimiento */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Métricas de Rendimiento
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Uptime */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Tiempo Operativo (Uptime)</span>
                <span className="text-sm font-bold">{uptime}%</span>
              </div>
              <Progress value={uptime} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">
                Últimos 30 días
              </p>
            </div>

            {/* Eficiencia */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Eficiencia Operacional</span>
                <span className="text-sm font-bold">{efficiency}%</span>
              </div>
              <Progress value={efficiency} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">
                Rendimiento vs. capacidad nominal
              </p>
            </div>

            {/* Disponibilidad */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Disponibilidad</span>
                <span className="text-sm font-bold">{metricas.availability}%</span>
              </div>
              <Progress 
                value={metricas.availability} 
                className="h-2" 
              />
              <p className="text-xs text-muted-foreground mt-1">
                Estado actual de disponibilidad
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Historial de Mantenimiento */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Wrench className="h-5 w-5" />
              Mantenimiento
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div className="flex items-center gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">Último Mantenimiento</p>
                  <p className="text-xs text-muted-foreground">
                    {mantenimiento.ultimo_mantenimiento || 'No registrado'}
                  </p>
                </div>
              </div>
              <CheckCircle className="h-5 w-5 text-green-600" />
            </div>

            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center gap-3">
                <Clock className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-sm font-medium">Próximo Mantenimiento</p>
                  <p className="text-xs text-muted-foreground">
                    {mantenimiento.proximo_mantenimiento || 'Por programar'}
                  </p>
                </div>
              </div>
              <Badge variant="outline" className="bg-white">
                {mantenimiento.dias_desde_ultimo > 0 ? `${30 - mantenimiento.dias_desde_ultimo} días` : 'Pendiente'}
              </Badge>
            </div>

            {mantenimiento.ordenes_pendientes > 0 && (
              <div className="flex items-center gap-3 p-3 bg-red-50 rounded-lg border border-red-200">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <div>
                  <p className="text-sm font-medium text-red-900">
                    {mantenimiento.ordenes_pendientes} {mantenimiento.ordenes_pendientes === 1 ? 'Orden Pendiente' : 'Órdenes Pendientes'}
                  </p>
                  <p className="text-xs text-red-700">Requiere atención</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Indicadores Visuales */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Gauge className="h-5 w-5" />
              Indicadores Clave
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="text-3xl font-bold text-green-600 mb-1">
                  {fallas.fallas_activas}
                </div>
                <p className="text-xs text-muted-foreground">Fallas Activas</p>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="text-3xl font-bold text-blue-600 mb-1">
                  {mantenimiento.dias_desde_ultimo}
                </div>
                <p className="text-xs text-muted-foreground">Días Operando</p>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg border border-purple-200">
                <div className="text-3xl font-bold text-purple-600 mb-1">
                  {mantenimiento.horas_mantenimiento.toFixed(1)}
                </div>
                <p className="text-xs text-muted-foreground">Horas de Mant.</p>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg border border-orange-200">
                <div className="text-3xl font-bold text-orange-600 mb-1">
                  {metricas.oee_score.toFixed(0)}
                </div>
                <p className="text-xs text-muted-foreground">Score OEE</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Acciones Rápidas */}
        <div className="space-y-2">
          <div className="flex gap-2">
            <Button className="flex-1" variant="default">
              <Wrench className="h-4 w-4 mr-2" />
              Programar Mantenimiento
            </Button>
            <Button className="flex-1" variant="outline">
              <Activity className="h-4 w-4 mr-2" />
              Ver Historial
            </Button>
          </div>
          <Button 
            className="w-full" 
            variant="outline"
            onClick={() => handleExportPDF()}
          >
            <Download className="h-4 w-4 mr-2" />
            Exportar Reporte PDF
          </Button>
        </div>
      </div>
    </div>
  );

  function handleExportPDF() {
    // Crear contenido del reporte
    const reportContent = `
REPORTE DE EQUIPO - ${equipo.nombre}
${'='.repeat(60)}

INFORMACIÓN GENERAL
Código: ${equipo.codigo}
Nombre: ${equipo.nombre}
Marca: ${equipo.marca}
Modelo: ${equipo.modelo}
Categoría: ${equipo.categoria}
Ubicación: ${equipo.ubicacion}
Estado: ${estado.nombre}

MÉTRICAS DE RENDIMIENTO
Índice de Salud: ${healthScore}%
Tiempo Operativo (Uptime): ${uptime}%
Eficiencia Operacional: ${efficiency}%
Disponibilidad: ${metricas.availability}%
Score OEE: ${metricas.oee_score}%

MANTENIMIENTO
Total de Órdenes: ${mantenimiento.total_ordenes}
Órdenes Completadas: ${mantenimiento.ordenes_completadas}
Órdenes Pendientes: ${mantenimiento.ordenes_pendientes}
Horas de Mantenimiento: ${mantenimiento.horas_mantenimiento.toFixed(1)}h
Días desde último mantenimiento: ${mantenimiento.dias_desde_ultimo}
Último Mantenimiento: ${mantenimiento.ultimo_mantenimiento || 'No registrado'}
Próximo Mantenimiento: ${mantenimiento.proximo_mantenimiento || 'Por programar'}

FALLAS
Fallas Activas: ${fallas.fallas_activas}
Fallas (últimos 30 días): ${fallas.fallas_30_dias}

${'='.repeat(60)}
Generado: ${new Date().toLocaleString('es-CL')}
Sistema CMMS Somacor V2
    `;

    // Crear blob y descargar
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reporte_${equipo.codigo}_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }
};

export default EquipmentDetailPanel;
