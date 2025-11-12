import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageLayout, PageHeader } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { 
  ArrowLeft, 
  Edit, 
  Wrench, 
  Calendar, 
  MapPin, 
  Tag,
  CheckCircle,
  Clock,
  XCircle,
  AlertTriangle,
  FileText,
  Activity
} from 'lucide-react';
import { equiposService, ordenesTrabajoService, checklistService } from '@/services/apiService';

interface EquipoDetalle {
  id: number;
  codigo: string;
  nombre: string;
  marca: string;
  modelo: string;
  patente: string;
  ubicacion: string;
  estado: string;
  categoria: string;
  horometro?: number;
  anio_fabricacion?: string;
  numero_serie?: string;
  activo: boolean;
}

export default function EquipoDetalleView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [equipo, setEquipo] = useState<EquipoDetalle | null>(null);
  const [ordenes, setOrdenes] = useState<any[]>([]);
  const [checklists, setChecklists] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadEquipoData();
    }
  }, [id]);

  const loadEquipoData = async () => {
    try {
      setLoading(true);
      setError(null);

      const equipoData = await equiposService.getById(Number(id));
      
      const equipoTransformado = {
        id: equipoData.idequipo || equipoData.id,
        codigo: equipoData.codigointerno || equipoData.codigo,
        nombre: equipoData.nombreequipo || equipoData.nombre,
        marca: equipoData.marca || '',
        modelo: equipoData.modelo || '',
        patente: equipoData.patente || '',
        ubicacion: equipoData.faena_nombre || equipoData.ubicacion || 'Sin ubicación',
        estado: equipoData.estado_nombre || equipoData.estado || 'Sin estado',
        categoria: equipoData.tipo_equipo_nombre || equipoData.categoria || 'Sin categoría',
        horometro: equipoData.horometro,
        anio_fabricacion: equipoData.anio_fabricacion,
        numero_serie: equipoData.numero_serie,
        activo: equipoData.activo !== undefined ? equipoData.activo : true
      };

      setEquipo(equipoTransformado);

      // Cargar órdenes de trabajo del equipo
      try {
        const ordenesData = await ordenesTrabajoService.getByEquipment(Number(id));
        setOrdenes(ordenesData.slice(0, 10)); // Últimas 10 órdenes
      } catch (err) {
        console.error('Error cargando órdenes:', err);
        setOrdenes([]);
      }

      // Cargar historial de checklists
      try {
        const checklistsData = await checklistService.getHistorialEquipo(Number(id));
        setChecklists(checklistsData.slice(0, 10)); // Últimos 10 checklists
      } catch (err) {
        console.error('Error cargando checklists:', err);
        setChecklists([]);
      }

    } catch (err) {
      console.error('Error loading equipo:', err);
      setError('Error al cargar los detalles del equipo');
    } finally {
      setLoading(false);
    }
  };

  const getEstadoColor = (estado: string) => {
    switch (estado?.toLowerCase()) {
      case 'operativo':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100';
      case 'en mantenimiento':
      case 'en mantencion':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100';
      case 'fuera de servicio':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100';
    }
  };

  const getEstadoIcon = (estado: string) => {
    switch (estado?.toLowerCase()) {
      case 'operativo':
        return <CheckCircle className="h-4 w-4" />;
      case 'en mantenimiento':
      case 'en mantencion':
        return <Clock className="h-4 w-4" />;
      case 'fuera de servicio':
        return <XCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Cargando detalles del equipo...</p>
          </div>
        </div>
      </PageLayout>
    );
  }

  if (error || !equipo) {
    return (
      <PageLayout>
        <PageHeader
          title="Error"
          description={error || 'Equipo no encontrado'}
        />
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <p className="text-muted-foreground mb-4">{error || 'El equipo solicitado no existe'}</p>
              <Button onClick={() => navigate('/equipos')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Volver a Equipos
              </Button>
            </div>
          </CardContent>
        </Card>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader
        title={equipo.nombre}
        description={`Código: ${equipo.codigo}`}
        action={
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate('/equipos')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Volver
            </Button>
            <Button onClick={() => navigate(`/equipos/${id}/editar`)}>
              <Edit className="h-4 w-4 mr-2" />
              Editar
            </Button>
          </div>
        }
      />

      {/* Información General */}
      <Card>
        <CardHeader>
          <CardTitle>Información General</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="flex items-start gap-3">
              <Tag className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Código Interno</p>
                <p className="font-medium">{equipo.codigo}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Wrench className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Marca / Modelo</p>
                <p className="font-medium">{equipo.marca} {equipo.modelo}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Patente</p>
                <p className="font-medium">{equipo.patente || 'N/A'}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <MapPin className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Ubicación</p>
                <p className="font-medium">{equipo.ubicacion}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Activity className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Estado</p>
                <Badge className={`${getEstadoColor(equipo.estado)} flex items-center gap-1 w-fit mt-1`}>
                  {getEstadoIcon(equipo.estado)}
                  {equipo.estado}
                </Badge>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Tag className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm text-muted-foreground">Categoría</p>
                <p className="font-medium">{equipo.categoria}</p>
              </div>
            </div>

            {equipo.horometro && (
              <div className="flex items-start gap-3">
                <Clock className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm text-muted-foreground">Horómetro</p>
                  <p className="font-medium">{equipo.horometro.toLocaleString()} hrs</p>
                </div>
              </div>
            )}

            {equipo.anio_fabricacion && (
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm text-muted-foreground">Año Fabricación</p>
                  <p className="font-medium">{equipo.anio_fabricacion}</p>
                </div>
              </div>
            )}

            {equipo.numero_serie && (
              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm text-muted-foreground">Número de Serie</p>
                  <p className="font-medium">{equipo.numero_serie}</p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Tabs con historial */}
      <Tabs defaultValue="ordenes" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="ordenes">Órdenes de Trabajo</TabsTrigger>
          <TabsTrigger value="checklists">Historial Checklists</TabsTrigger>
        </TabsList>

        <TabsContent value="ordenes">
          <Card>
            <CardHeader>
              <CardTitle>Órdenes de Trabajo Recientes</CardTitle>
              <CardDescription>Últimas 10 órdenes de trabajo del equipo</CardDescription>
            </CardHeader>
            <CardContent>
              {ordenes.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No hay órdenes de trabajo registradas</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Número OT</TableHead>
                      <TableHead>Descripción</TableHead>
                      <TableHead>Estado</TableHead>
                      <TableHead>Prioridad</TableHead>
                      <TableHead>Fecha</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {ordenes.map((orden) => (
                      <TableRow key={orden.idordentrabajo}>
                        <TableCell className="font-medium">{orden.numeroot}</TableCell>
                        <TableCell>{orden.descripcionproblemareportado}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{orden.estado_nombre}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{orden.prioridad}</Badge>
                        </TableCell>
                        <TableCell>
                          {new Date(orden.fechareportefalla).toLocaleDateString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="checklists">
          <Card>
            <CardHeader>
              <CardTitle>Historial de Checklists</CardTitle>
              <CardDescription>Últimos 10 checklists realizados al equipo</CardDescription>
            </CardHeader>
            <CardContent>
              {checklists.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No hay checklists registrados</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Fecha</TableHead>
                      <TableHead>Template</TableHead>
                      <TableHead>Operador</TableHead>
                      <TableHead>Conformidad</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {checklists.map((checklist) => (
                      <TableRow key={checklist.id}>
                        <TableCell>
                          {new Date(checklist.fecha_realizacion).toLocaleDateString()}
                        </TableCell>
                        <TableCell>{checklist.template_nombre || 'N/A'}</TableCell>
                        <TableCell>{checklist.operador_nombre || 'N/A'}</TableCell>
                        <TableCell>
                          <Badge 
                            className={checklist.conforme ? 
                              'bg-green-100 text-green-800' : 
                              'bg-red-100 text-red-800'
                            }
                          >
                            {checklist.conforme ? 'Conforme' : 'No Conforme'}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </PageLayout>
  );
}
