import React, { useState, useEffect, useMemo } from 'react';
import { AlertCircle, Send, UploadCloud, CheckSquare, Clock, User, Calendar, Wrench } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import MultipleImageUpload from '@/components/MultipleImageUpload';
import apiClient from '@/api/apiClient';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

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

const ChecklistDiarioView: React.FC = () => {
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [selectedEquipoId, setSelectedEquipoId] = useState<string>('');
  const [template, setTemplate] = useState<ChecklistTemplate | null>(null);
  const [responses, setResponses] = useState<ChecklistResponse>({});
  const [generalInfo, setGeneralInfo] = useState<GeneralInfo>({
    horometro_inspeccion: '',
    lugar_inspeccion: '',
  });
  const [images, setImages] = useState<ImageData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [currentDate, setCurrentDate] = useState('');

  useEffect(() => {
    const today = new Date();
    const formattedDate = today.toISOString().split('T')[0];
    setCurrentDate(formattedDate);
    
    const fetchEquipos = async () => {
      setIsLoading(true);
      try {
        const response = await apiClient.get('v2/equipos/');
        setEquipos(response.data.results || response.data);
      } catch (err) {
        setError('Error al cargar la lista de equipos. Por favor, intente de nuevo.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchEquipos();
  }, []);

  useEffect(() => {
    if (!selectedEquipoId) {
      setTemplate(null);
      return;
    }

    const fetchChecklistTemplate = async () => {
      setIsLoading(true);
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
        setIsLoading(false);
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

    // Preparar imágenes para el payload
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
    } catch (err: any) {
      const errorData = err.response?.data;
      const errorMessage = typeof errorData === 'object' ? JSON.stringify(errorData) : err.message;
      setError(`Error al enviar el checklist: ${errorMessage}`);
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading && !template) {
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
        title="Checklist Diario" 
        subtitle="Formulario de inspección diaria de equipos"
      />

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
            <Select value={selectedEquipoId} onValueChange={setSelectedEquipoId} disabled={isLoading}>
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
    </PageLayout>
  );
};

export default ChecklistDiarioView;