import React, { useState, useEffect, useMemo } from 'react';
import { 
  ClipboardCheck, Plus, Search, CheckCircle, XCircle, Clock, User, Calendar, 
  Wrench, FileText, Camera, Send, Save, Edit, Trash2, Eye, AlertTriangle,
  AlertCircle, UploadCloud, CheckSquare, Filter
} from 'lucide-react';
import { PageLayout, PageHeader, StatsGrid, ContentGrid } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import CreateChecklistForm from '@/components/forms/CreateChecklistForm';
import MultipleImageUpload from '@/components/MultipleImageUpload';
import { checklistService } from '@/services/checklistService';
import apiClient from '@/api/apiClient';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface Checklist {
  id: number;
  name: string;
  equipment: string;
  equipmentCode: string;
  technician: string;
  date: string;
  status: 'pendiente' | 'en_progreso' | 'completado' | 'cancelado';
  totalItems: number;
  completedItems: number;
  failedItems: number;
  observations?: string;
  images?: string[];
  createdAt: string;
  completedAt?: string;
}

interface ChecklistStats {
  totalChecklists: number;
  pendingChecklists: number;
  inProgressChecklists: number;
  completedChecklists: number;
  averageCompletion: number;
}

interface Equipo {
  idequipo: number;
  nombreequipo: string;
  codigointerno: string;
  idtipoequipo: number;
}

interface ChecklistItem {
  id_item: number;
  texto: string;
  es_critico: boolean;
  orden: number;
}

interface ChecklistCategory {
  id_category: number;
  nombre: string;
  orden: number;
  items: ChecklistItem[];
}

interface ChecklistTemplate {
  id_template: number;
  nombre: string;
  tipo_equipo_nombre: string;
  categories: ChecklistCategory[];
}

interface ChecklistResponse {
  [key: number]: {
    estado: 'bueno' | 'malo' | 'na' | '';
    observacion_item: string;
  };
}

interface GeneralInfo {
  [key: string]: string | number;
}

interface ImageData {
  id: string;
  descripcion: string;
  imagen_base64: string;
  preview?: string;
}

// =================================================================================
// COMPONENTE PRINCIPAL
// =================================================================================

const ChecklistUnificadoView: React.FC = () => {
  // Estados para la pestaña de lista de checklists
  const [checklists, setChecklists] = useState<Checklist[]>([]);
  const [stats, setStats] = useState<ChecklistStats | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [equipmentFilter, setEquipmentFilter] = useState('all');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedChecklist, setSelectedChecklist] = useState<Checklist | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  // Estados para la pestaña de checklist diario
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [selectedEquipoId, setSelectedEquipoId] = useState<string>('');
  const [template, setTemplate] = useState<ChecklistTemplate | null>(null);
  const [responses, setResponses] = useState<ChecklistResponse>({});
  const [generalInfo, setGeneralInfo] = useState<GeneralInfo>({
    horometro_inspeccion: '',
    lugar_inspeccion: '',
  });
  const [images, setImages] = useState<ImageData[]>([]);
  const [currentDate, setCurrentDate] = useState('');
  
  // Estados generales
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('lista');

  // Datos mock para la lista de checklists
  const mockChecklists: Checklist[] = [
    {
      id: 1,
      name: 'Checklist Diario Compresor A-101',
      equipment: 'Compresor de Aire Principal',
      equipmentCode: 'EQ-001',
      technician: 'Juan Pérez',
      date: '2024-10-15',
      status: 'completado',
      totalItems: 15,
      completedItems: 14,
      failedItems: 1,
      observations: 'Equipo en buen estado general, se detectó fuga menor en válvula de drenaje',
      images: ['checklist_1.jpg', 'valve_leak.jpg'],
      createdAt: '2024-10-15',
      completedAt: '2024-10-15'
    },
    {
      id: 2,
      name: 'Checklist Semanal Bomba B-205',
      equipment: 'Bomba Centrífuga B-205',
      equipmentCode: 'EQ-002',
      technician: 'María García',
      date: '2024-10-16',
      status: 'en_progreso',
      totalItems: 12,
      completedItems: 8,
      failedItems: 0,
      createdAt: '2024-10-16'
    },
    {
      id: 3,
      name: 'Checklist Mensual Motor C-310',
      equipment: 'Motor Eléctrico C-310',
      equipmentCode: 'EQ-003',
      technician: 'Carlos López',
      date: '2024-10-17',
      status: 'pendiente',
      totalItems: 20,
      completedItems: 0,
      failedItems: 0,
      createdAt: '2024-10-17'
    }
  ];

  const mockStats: ChecklistStats = {
    totalChecklists: 24,
    pendingChecklists: 8,
    inProgressChecklists: 5,
    completedChecklists: 11,
    averageCompletion: 85
  };

  // Cargar datos iniciales
  useEffect(() => {
    const today = new Date();
    const formattedDate = today.toISOString().split('T')[0];
    setCurrentDate(formattedDate);
    
    fetchChecklistsData();
    fetchEquipos();
  }, []);

  const fetchChecklistsData = async () => {
    try {
      setLoading(true);
      setError('');
      // TODO: Cargar datos reales del backend
      setChecklists(mockChecklists);
      setStats(mockStats);
    } catch (err) {
      console.error("Error fetching checklists data:", err);
      setError("No se pudo cargar la información de checklists.");
    } finally {
      setLoading(false);
    }
  };

  const fetchEquipos = async () => {
    try {
      const response = await apiClient.get('v2/equipos/');
      setEquipos(response.data.results || response.data);
    } catch (err) {
      console.error('Error al cargar equipos:', err);
    }
  };

  // Cargar template cuando se selecciona un equipo
  useEffect(() => {
    if (!selectedEquipoId) {
      setTemplate(null);
      return;
    }

    const fetchChecklistTemplate = async () => {
      setLoading(true);
      setError(null);
      setSubmitSuccess(null);
      setTemplate(null);
      try {
        const response = await apiClient.get(`v2/checklist-workflow/templates-por-equipo/${selectedEquipoId}/`);
        const templateData = response.data.templates?.[0];
        if (templateData) {
          setTemplate(templateData);
          initializeFormState(templateData);
        } else {
          setError(`No se encontró un checklist para el equipo seleccionado.`);
        }
      } catch (err) {
        setError('Error al cargar el checklist. Verifique que exista una plantilla para este tipo de equipo.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchChecklistTemplate();
  }, [selectedEquipoId]);

  const initializeFormState = (templateData: ChecklistTemplate) => {
    const initialResponses: ChecklistResponse = {};
    templateData.categories.forEach(category => {
      category.items.forEach(item => {
        initialResponses[item.id_item] = { estado: '', observacion_item: '' };
      });
    });
    setResponses(initialResponses);
    setGeneralInfo({
      horometro_inspeccion: '',
      lugar_inspeccion: '',
    });
    setImages([]);
    setError(null);
    setSubmitSuccess(null);
  };

  // Handlers para checklist diario
  const handleResponseChange = (itemId: number, estado: 'bueno' | 'malo' | 'na', observacion: string | null = null) => {
    setResponses(prev => ({
      ...prev,
      [itemId]: {
        estado: estado,
        observacion_item: observacion !== null ? observacion : prev[itemId]?.observacion_item || '',
      },
    }));
  };

  const handleGeneralInfoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setGeneralInfo(prev => ({ ...prev, [name]: value }));
  };

  const selectedEquipo = useMemo(() => {
    return equipos.find(e => e.idequipo === parseInt(selectedEquipoId, 10));
  }, [selectedEquipoId, equipos]);

  const criticalItemsInBadState = useMemo(() => {
    if (!template) return [];
    return template.categories.flatMap(cat => cat.items)
      .filter(item => item.es_critico && responses[item.id_item]?.estado === 'malo');
  }, [template, responses]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!template || !selectedEquipo) {
      setError("No se puede enviar el formulario sin un equipo y checklist seleccionados.");
      return;
    }
    
    if (!generalInfo.horometro_inspeccion) {
      setError("Debe ingresar el horómetro/kilometraje.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setSubmitSuccess(null);
    
    const answersPayload = template.categories.flatMap(cat => cat.items).map(item => {
      const response = responses[item.id_item];
      return {
        item: item.id_item,
        estado: response?.estado || 'na',
        observacion_item: response?.observacion_item || '',
      };
    });

    const imagenesPayload = images.map(img => ({
      descripcion: img.descripcion,
      imagen_base64: img.imagen_base64
    }));

    const payload = {
      template: template.id_template,
      equipo: selectedEquipo.idequipo,
      fecha_inspeccion: currentDate,
      horometro_inspeccion: Number(generalInfo.horometro_inspeccion),
      lugar_inspeccion: generalInfo.lugar_inspeccion as string,
      answers: answersPayload,
      imagenes: imagenesPayload,
    };
    
    try {
      await apiClient.post('v2/checklist-workflow/completar-checklist/', payload);
      setSubmitSuccess('Checklist enviado con éxito.');
      setSelectedEquipoId('');
      // Cambiar a la pestaña de lista y recargar
      setActiveTab('lista');
      fetchChecklistsData();
    } catch (err: any) {
      const errorData = err.response?.data;
      const errorMessage = typeof errorData === 'object' ? JSON.stringify(errorData) : err.message;
      setError(`Error al enviar el checklist: ${errorMessage}`);
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handlers para lista de checklists
  const filteredChecklists = checklists.filter(checklist => {
    const matchesSearch = checklist.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         checklist.equipment.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         checklist.equipmentCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         checklist.technician.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || checklist.status === statusFilter;
    const matchesEquipment = equipmentFilter === 'all' || checklist.equipmentCode === equipmentFilter;
    
    return matchesSearch && matchesStatus && matchesEquipment;
  });

  const handleViewDetails = (checklist: Checklist) => {
    setSelectedChecklist(checklist);
    console.log('Ver detalles de:', checklist.name);
  };

  const handleEdit = (checklist: Checklist) => {
    setSelectedChecklist(checklist);
    console.log('Editar checklist:', checklist.name);
  };

  const handleDelete = (checklist: Checklist) => {
    setSelectedChecklist(checklist);
    setShowDeleteDialog(true);
  };

  const confirmDelete = () => {
    if (selectedChecklist) {
      console.log('Eliminar checklist:', selectedChecklist.name);
      setShowDeleteDialog(false);
      setSelectedChecklist(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pendiente':
        return <Badge variant="secondary"><Clock className="h-3 w-3 mr-1" />Pendiente</Badge>;
      case 'en_progreso':
        return <Badge variant="default" className="bg-blue-100 text-blue-800"><ClipboardCheck className="h-3 w-3 mr-1" />En Progreso</Badge>;
      case 'completado':
        return <Badge variant="default" className="bg-green-100 text-green-800"><CheckCircle className="h-3 w-3 mr-1" />Completado</Badge>;
      case 'cancelado':
        return <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" />Cancelado</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getCompletionPercentage = (completed: number, total: number) => {
    return total > 0 ? Math.round((completed / total) * 100) : 0;
  };

  const getProgressBadge = (completed: number, total: number) => {
    const percentage = getCompletionPercentage(completed, total);
    if (percentage === 100) {
      return <Badge variant="default" className="bg-green-100 text-green-800">{percentage}%</Badge>;
    } else if (percentage >= 75) {
      return <Badge variant="default" className="bg-blue-100 text-blue-800">{percentage}%</Badge>;
    } else if (percentage >= 50) {
      return <Badge variant="default" className="bg-yellow-100 text-yellow-800">{percentage}%</Badge>;
    } else {
      return <Badge variant="default" className="bg-red-100 text-red-800">{percentage}%</Badge>;
    }
  };

  if (loading && activeTab === 'lista') {
    return (
      <PageLayout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader 
        title="Gestión de Checklists" 
        subtitle="Administra y ejecuta checklists de mantenimiento"
      >
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Checklist
        </Button>
      </PageHeader>

      {/* Tarjetas de estadísticas */}
      <StatsGrid>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Checklists</CardTitle>
            <ClipboardCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalChecklists}</div>
            <p className="text-xs text-muted-foreground">Checklists registrados</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pendientes</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats?.pendingChecklists}</div>
            <p className="text-xs text-muted-foreground">Requieren ejecución</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">En Progreso</CardTitle>
            <ClipboardCheck className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.inProgressChecklists}</div>
            <p className="text-xs text-muted-foreground">Activamente en ejecución</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completados</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.completedChecklists}</div>
            <p className="text-xs text-muted-foreground">
              {stats ? Math.round((stats.completedChecklists / stats.totalChecklists) * 100) : 0}% del total
            </p>
          </CardContent>
        </Card>
      </StatsGrid>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="lista" className="flex items-center gap-2">
            <ClipboardCheck className="h-4 w-4" />
            Lista de Checklists ({checklists.length})
          </TabsTrigger>
          <TabsTrigger value="nuevo" className="flex items-center gap-2">
            <CheckSquare className="h-4 w-4" />
            Ejecutar Checklist Diario
          </TabsTrigger>
        </TabsList>

        {/* Tab: Lista de Checklists */}
        <TabsContent value="lista" className="space-y-4">
          <ContentGrid>
            <Card>
              <CardHeader>
                <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
                  <div>
                    <CardTitle>Lista de Checklists</CardTitle>
                    <CardDescription>Listas de verificación y seguimiento de mantenimiento</CardDescription>
                  </div>
                  
                  <div className="flex flex-col md:flex-row gap-2 w-full md:w-auto">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Buscar checklist..."
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
                        <SelectItem value="pendiente">Pendiente</SelectItem>
                        <SelectItem value="en_progreso">En Progreso</SelectItem>
                        <SelectItem value="completado">Completado</SelectItem>
                        <SelectItem value="cancelado">Cancelado</SelectItem>
                      </SelectContent>
                    </Select>

                    <Select value={equipmentFilter} onValueChange={setEquipmentFilter}>
                      <SelectTrigger className="w-full md:w-48">
                        <SelectValue placeholder="Equipo" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Todos los equipos</SelectItem>
                        <SelectItem value="EQ-001">EQ-001</SelectItem>
                        <SelectItem value="EQ-002">EQ-002</SelectItem>
                        <SelectItem value="EQ-003">EQ-003</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredChecklists.map(checklist => (
                    <div key={checklist.id} className="border rounded-lg p-4 hover:bg-muted/50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="font-medium">{checklist.name}</h4>
                            {getStatusBadge(checklist.status)}
                            {getProgressBadge(checklist.completedItems, checklist.totalItems)}
                          </div>
                          
                          <div className="text-sm text-muted-foreground space-y-1">
                            <div className="flex items-center gap-2">
                              <Wrench className="h-3 w-3" />
                              {checklist.equipment} ({checklist.equipmentCode})
                            </div>
                            <div className="flex items-center gap-2">
                              <User className="h-3 w-3" />
                              Técnico: {checklist.technician}
                            </div>
                            <div className="flex items-center gap-2">
                              <Calendar className="h-3 w-3" />
                              Fecha: {checklist.date}
                            </div>
                            <div className="flex items-center gap-2">
                              <FileText className="h-3 w-3" />
                              Items: {checklist.completedItems}/{checklist.totalItems} completados
                              {checklist.failedItems > 0 && (
                                <span className="text-red-600">({checklist.failedItems} fallos)</span>
                              )}
                            </div>
                            {checklist.images && checklist.images.length > 0 && (
                              <div className="flex items-center gap-2">
                                <Camera className="h-3 w-3" />
                                {checklist.images.length} imagen(es) adjunta(s)
                              </div>
                            )}
                          </div>
                          
                          {checklist.observations && (
                            <div className="mt-3 p-2 bg-muted/50 rounded text-sm">
                              <strong>Observaciones:</strong> {checklist.observations}
                            </div>
                          )}
                          
                          <div className="mt-3">
                            <div className="flex justify-between text-xs text-muted-foreground mb-1">
                              <span>Progreso</span>
                              <span>{getCompletionPercentage(checklist.completedItems, checklist.totalItems)}%</span>
                            </div>
                            <div className="w-full bg-muted rounded-full h-2">
                              <div 
                                className="bg-primary h-2 rounded-full transition-all duration-300"
                                style={{ width: `${getCompletionPercentage(checklist.completedItems, checklist.totalItems)}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex gap-1 ml-4">
                          <Button variant="outline" size="sm" onClick={() => handleViewDetails(checklist)} title="Ver detalles">
                            <Eye className="h-3 w-3" />
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => handleEdit(checklist)} title="Editar">
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => handleDelete(checklist)} title="Eliminar">
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {filteredChecklists.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <ClipboardCheck className="mx-auto h-12 w-12 text-muted-foreground/50" />
                      <h3 className="mt-2 text-sm font-medium">No se encontraron checklists</h3>
                      <p className="mt-1 text-sm">No hay checklists que coincidan con los filtros seleccionados.</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </ContentGrid>
        </TabsContent>

        {/* Tab: Ejecutar Checklist Diario */}
        <TabsContent value="nuevo" className="space-y-4">
          <div className="max-w-6xl mx-auto space-y-6">
            {/* Selección de equipo */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckSquare className="h-5 w-5" />
                  1. Seleccionar Equipo
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Select value={selectedEquipoId} onValueChange={setSelectedEquipoId} disabled={loading}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="-- Por favor, seleccione un equipo --" />
                  </SelectTrigger>
                  <SelectContent>
                    {equipos.map(equipo => (
                      <SelectItem key={equipo.idequipo} value={equipo.idequipo.toString()}>
                        {equipo.nombreequipo} ({equipo.codigointerno})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            {/* Mensajes de error y éxito */}
            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded-md" role="alert">
                <div className="flex items-center">
                  <AlertCircle className="h-5 w-5 mr-2" />
                  <div>
                    <p className="font-bold">Error</p>
                    <p>{error}</p>
                  </div>
                </div>
              </div>
            )}
            
            {submitSuccess && (
              <div className="bg-green-50 border-l-4 border-green-500 text-green-700 p-4 rounded-md" role="alert">
                <div className="flex items-center">
                  <CheckSquare className="h-5 w-5 mr-2" />
                  <div>
                    <p className="font-bold">Éxito</p>
                    <p>{submitSuccess}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Formulario de checklist */}
            {template && selectedEquipo && (
              <form onSubmit={handleSubmit}>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-2xl text-blue-700">{template.nombre}</CardTitle>
                    <CardDescription className="flex items-center gap-2">
                      <Wrench className="h-4 w-4" />
                      Equipo: {selectedEquipo.nombreequipo}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-8">
                    {/* Información General */}
                    <div className="p-4 border rounded-lg bg-gray-50">
                      <h3 className="font-bold text-lg text-gray-700 mb-4 flex items-center gap-2">
                        <User className="h-5 w-5" />
                        2. Información General
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <Label htmlFor="fecha" className="flex items-center gap-2">
                            <Calendar className="h-4 w-4" />
                            Fecha
                          </Label>
                          <Input 
                            type="date" 
                            id="fecha" 
                            name="fecha" 
                            value={currentDate} 
                            readOnly 
                            className="bg-gray-100" 
                          />
                        </div>
                        <div>
                          <Label htmlFor="horometro_inspeccion">
                            Horómetro / Km Actual *
                          </Label>
                          <Input 
                            type="number" 
                            id="horometro_inspeccion" 
                            name="horometro_inspeccion" 
                            value={generalInfo.horometro_inspeccion} 
                            onChange={handleGeneralInfoChange} 
                            required 
                          />
                        </div>
                        <div>
                          <Label htmlFor="lugar_inspeccion">
                            Lugar de Inspección
                          </Label>
                          <Input 
                            type="text" 
                            id="lugar_inspeccion" 
                            name="lugar_inspeccion" 
                            value={generalInfo.lugar_inspeccion as string} 
                            onChange={handleGeneralInfoChange} 
                          />
                        </div>
                      </div>
                    </div>

                    {/* Checklists */}
                    <div>
                      <h3 className="font-bold text-lg text-gray-700 mb-2 flex items-center gap-2">
                        <CheckSquare className="h-5 w-5" />
                        3. Chequear Estado de Operatividad
                      </h3>
                      <p className="text-sm text-gray-600 mb-4">(B=Bueno / M=Malo / NA=No Aplica)</p>
                      <div className="space-y-6">
                        {template.categories.sort((a,b) => a.orden - b.orden).map(category => (
                          <Card key={category.id_category}>
                            <CardHeader className="pb-3">
                              <CardTitle className="text-md bg-gray-100 p-2 rounded">
                                {category.nombre}
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                  <thead className="bg-gray-50">
                                    <tr>
                                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Ítem a Revisar
                                      </th>
                                      <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-40">
                                        Estado
                                      </th>
                                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Observaciones
                                      </th>
                                    </tr>
                                  </thead>
                                  <tbody className="bg-white divide-y divide-gray-200">
                                    {category.items.sort((a,b) => a.orden - b.orden).map(item => (
                                      <tr key={item.id_item} className={responses[item.id_item]?.estado === 'malo' ? 'bg-red-50' : ''}>
                                        <td className="px-4 py-2">
                                          <div className="flex items-center gap-2">
                                            <span className="text-sm text-gray-900">{item.texto}</span>
                                            {item.es_critico && (
                                              <Badge variant="destructive" className="text-xs">
                                                <AlertCircle className="h-3 w-3 mr-1" />
                                                Crítico
                                              </Badge>
                                            )}
                                          </div>
                                        </td>
                                        <td className="px-4 py-2 text-center">
                                          <div className="flex justify-center space-x-2">
                                            {['bueno', 'malo', 'na'].map(estado => (
                                              <label key={estado} className="flex items-center cursor-pointer">
                                                <input
                                                  type="radio"
                                                  name={`item_${item.id_item}`}
                                                  value={estado}
                                                  checked={responses[item.id_item]?.estado === estado}
                                                  onChange={() => handleResponseChange(item.id_item, estado as 'bueno' | 'malo' | 'na')}
                                                  className="mr-1"
                                                />
                                                <span className="text-xs font-medium">
                                                  {estado === 'bueno' ? 'B' : estado === 'malo' ? 'M' : 'NA'}
                                                </span>
                                              </label>
                                            ))}
                                          </div>
                                        </td>
                                        <td className="px-4 py-2">
                                          <Input
                                            type="text"
                                            placeholder="Observaciones..."
                                            value={responses[item.id_item]?.observacion_item || ''}
                                            onChange={(e) => handleResponseChange(item.id_item, responses[item.id_item]?.estado as 'bueno' | 'malo' | 'na', e.target.value)}
                                            className="text-sm"
                                          />
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </div>

                    {/* Sección de imágenes */}
                    <div className="p-4 border rounded-lg bg-gray-50">
                      <h3 className="font-bold text-lg text-gray-700 mb-4 flex items-center gap-2">
                        <UploadCloud className="h-5 w-5" />
                        4. Evidencias Fotográficas
                      </h3>
                      <MultipleImageUpload
                        images={images}
                        onImagesChange={setImages}
                        maxImages={5}
                        maxSizeKB={2048}
                        disabled={isSubmitting}
                      />
                    </div>

                    {/* Alertas de elementos críticos */}
                    {criticalItemsInBadState.length > 0 && (
                      <div className="p-4 bg-red-50 border border-red-400 rounded-lg">
                        <div className="flex items-center mb-2">
                          <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
                          <h4 className="font-bold text-red-700">¡ATENCIÓN! Elementos Críticos en Mal Estado</h4>
                        </div>
                        <p className="text-red-700 text-sm mb-2">
                          Los siguientes elementos críticos están marcados como "Malo". 
                          El equipo NO PUEDE ser utilizado hasta que se reparen:
                        </p>
                        <ul className="list-disc list-inside text-red-700 text-sm">
                          {criticalItemsInBadState.map(item => (
                            <li key={item.id_item}>{item.texto}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Botón de envío */}
                    <div className="flex justify-end">
                      <Button
                        type="submit"
                        disabled={isSubmitting || criticalItemsInBadState.length > 0}
                        className={`
                          flex items-center gap-2 px-6 py-3
                          ${criticalItemsInBadState.length > 0 
                            ? 'bg-red-500 hover:bg-red-600 cursor-not-allowed' 
                            : ''
                          }
                        `}
                      >
                        {isSubmitting ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            Enviando...
                          </>
                        ) : criticalItemsInBadState.length > 0 ? (
                          <>
                            <AlertCircle className="h-4 w-4" />
                            No se puede enviar - Elementos críticos en mal estado
                          </>
                        ) : (
                          <>
                            <Send className="h-4 w-4" />
                            Enviar Checklist
                          </>
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </form>
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Formulario de creación de checklist */}
      <CreateChecklistForm
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={() => {
          fetchChecklistsData();
        }}
      />

      {/* Diálogo de confirmación de eliminación */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Estás seguro?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará permanentemente el checklist "{selectedChecklist?.name}".
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

export default ChecklistUnificadoView;
