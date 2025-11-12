import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  User, 
  Mail, 
  Phone, 
  Briefcase,
  Calendar,
  CheckCircle,
  Clock,
  Wrench,
  FileText,
  Award,
  TrendingUp
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import apiClient from '@/api/apiClient';

interface TecnicoDetalle {
  idtecnico: number;
  nombre_completo: string;
  username: string;
  first_name: string;
  last_name: string;
  telefono: string;
  email: string;
  email_usuario: string;
  cargo: string;
  estado: string;
  activo: boolean;
  fecha_ingreso: string;
  especialidades_list: string[];
  especialidades_detalle: Array<{
    idespecialidad: number;
    nombreespecialidad: string;
    descripcion: string;
  }>;
  ordenes_activas: number;
}

const TecnicoDetalleView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [tecnico, setTecnico] = useState<TecnicoDetalle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTecnicoDetalle();
  }, [id]);

  const fetchTecnicoDetalle = async () => {
    if (!id) {
      setError('ID de técnico no proporcionado');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const response = await apiClient.get(`/v2/tecnicos/${id}/`);
      setTecnico(response.data);
      console.log('✅ Detalle de técnico cargado:', response.data);
    } catch (err: any) {
      console.error('❌ Error cargando detalle de técnico:', err);
      setError('No se pudo cargar la información del técnico.');
    } finally {
      setLoading(false);
    }
  };

  const getEstadoBadge = (estado: string) => {
    switch (estado) {
      case 'disponible':
        return <Badge variant="default" className="bg-green-100 text-green-800">Disponible</Badge>;
      case 'ocupado':
        return <Badge variant="default" className="bg-yellow-100 text-yellow-800">Ocupado</Badge>;
      case 'no_disponible':
        return <Badge variant="destructive">No Disponible</Badge>;
      default:
        return <Badge variant="secondary">{estado}</Badge>;
    }
  };

  const getInitials = (firstName: string, lastName: string) => {
    return ((firstName?.[0] || '') + (lastName?.[0] || '')).toUpperCase() || 'T';
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

  if (error || !tecnico) {
    return (
      <PageLayout>
        <div className="p-8 text-center">
          <div className="text-destructive bg-destructive/10 rounded-lg p-6">
            {error || 'Técnico no encontrado'}
          </div>
          <Button 
            variant="outline" 
            onClick={() => navigate('/tecnicos')}
            className="mt-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver a Técnicos
          </Button>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader 
        title={`Perfil de ${tecnico.nombre_completo}`}
        subtitle={tecnico.cargo || 'Técnico'}
      >
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={() => navigate(`/tecnicos/${id}/editar`)}
          >
            Editar Perfil
          </Button>
          <Button 
            variant="outline" 
            onClick={() => navigate('/tecnicos')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Button>
        </div>
      </PageHeader>

      {/* Tarjetas de estadísticas */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Estado Actual</CardTitle>
            <User className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold mb-2">
              {getEstadoBadge(tecnico.estado)}
            </div>
            <p className="text-xs text-muted-foreground">
              {tecnico.activo ? 'Activo en el sistema' : 'Inactivo'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Órdenes Activas</CardTitle>
            <Wrench className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{tecnico.ordenes_activas}</div>
            <p className="text-xs text-muted-foreground">
              Órdenes en progreso
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Especialidades</CardTitle>
            <Award className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {tecnico.especialidades_list.length}
            </div>
            <p className="text-xs text-muted-foreground">
              Áreas de expertise
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Antigüedad</CardTitle>
            <Calendar className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {tecnico.fecha_ingreso ? new Date(tecnico.fecha_ingreso).toLocaleDateString('es-CL') : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              Fecha de ingreso
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Información del técnico */}
      <ContentGrid>
        <div className="grid gap-6 md:grid-cols-2">
          {/* Información Personal */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Información Personal
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 mb-6">
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary text-primary-foreground text-2xl font-bold">
                  {getInitials(tecnico.first_name, tecnico.last_name)}
                </div>
                <div>
                  <h3 className="text-xl font-semibold">{tecnico.nombre_completo}</h3>
                  <p className="text-sm text-muted-foreground">@{tecnico.username}</p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <Mail className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Email</p>
                    <p className="text-sm text-muted-foreground">
                      {tecnico.email || tecnico.email_usuario || 'No especificado'}
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Phone className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Teléfono</p>
                    <p className="text-sm text-muted-foreground">
                      {tecnico.telefono || 'No especificado'}
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Briefcase className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Cargo</p>
                    <p className="text-sm text-muted-foreground">
                      {tecnico.cargo || 'No especificado'}
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Fecha de Ingreso</p>
                    <p className="text-sm text-muted-foreground">
                      {tecnico.fecha_ingreso 
                        ? new Date(tecnico.fecha_ingreso).toLocaleDateString('es-CL', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                          })
                        : 'No especificado'}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Especialidades */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="h-5 w-5" />
                Especialidades Técnicas
              </CardTitle>
              <CardDescription>
                Áreas de expertise y certificaciones
              </CardDescription>
            </CardHeader>
            <CardContent>
              {tecnico.especialidades_detalle && tecnico.especialidades_detalle.length > 0 ? (
                <div className="space-y-3">
                  {tecnico.especialidades_detalle.map((esp) => (
                    <div 
                      key={esp.idespecialidad}
                      className="p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-sm">{esp.nombreespecialidad}</h4>
                          {esp.descripcion && (
                            <p className="text-xs text-muted-foreground mt-1">
                              {esp.descripcion}
                            </p>
                          )}
                        </div>
                        <CheckCircle className="h-4 w-4 text-green-600 mt-1" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Award className="mx-auto h-12 w-12 text-muted-foreground/50" />
                  <p className="mt-2 text-sm">No hay especialidades registradas</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Órdenes de Trabajo Activas */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wrench className="h-5 w-5" />
              Órdenes de Trabajo Activas
            </CardTitle>
            <CardDescription>
              Órdenes actualmente asignadas al técnico
            </CardDescription>
          </CardHeader>
          <CardContent>
            {tecnico.ordenes_activas > 0 ? (
              <div className="text-center py-8">
                <Wrench className="mx-auto h-12 w-12 text-blue-600" />
                <p className="mt-2 text-lg font-semibold">{tecnico.ordenes_activas} órdenes activas</p>
                <p className="text-sm text-muted-foreground mt-1">
                  El técnico tiene órdenes de trabajo en progreso
                </p>
                <Button 
                  variant="outline" 
                  className="mt-4"
                  onClick={() => navigate(`/ordenes-trabajo?tecnico=${id}`)}
                >
                  Ver Órdenes
                </Button>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <CheckCircle className="mx-auto h-12 w-12 text-green-600" />
                <p className="mt-2 text-sm font-medium">Sin órdenes activas</p>
                <p className="text-xs mt-1">El técnico está disponible para nuevas asignaciones</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Estadísticas y Desempeño */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Estadísticas y Desempeño
            </CardTitle>
            <CardDescription>
              Métricas de rendimiento del técnico
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              <TrendingUp className="mx-auto h-12 w-12 text-muted-foreground/50" />
              <p className="mt-2 text-sm">Estadísticas de desempeño</p>
              <p className="text-xs mt-1">Próximamente disponible</p>
            </div>
          </CardContent>
        </Card>
      </ContentGrid>
    </PageLayout>
  );
};

export default TecnicoDetalleView;
