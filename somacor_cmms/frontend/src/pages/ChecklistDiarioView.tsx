import React, { useState, useEffect } from 'react';
import { AlertCircle, Send, CheckSquare, Calendar } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout/PageLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/context/AuthContext';
import apiClient from '@/api/apiClient';

interface Equipo {
  idequipo: number;
  nombreequipo: string;
  codigointerno: string;
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

const ChecklistDiarioView: React.FC = () => {
  const { token, isLoading: authLoading } = useAuth();
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [selectedEquipoId, setSelectedEquipoId] = useState('');
  const [template, setTemplate] = useState<ChecklistTemplate | null>(null);
  const [responses, setResponses] = useState<Record<number, { estado: string; observacion: string }>>({});
  const [horometro, setHorometro] = useState('');
  const [lugar, setLugar] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [currentDate] = useState(new Date().toISOString().split('T')[0]);

  // Cargar equipos cuando el token esté disponible
  useEffect(() => {
    if (!token || authLoading) return;

    const fetchEquipos = async () => {
      try {
        const response = await apiClient.get('v2/equipos/');
        setEquipos(response.data.results || response.data);
      } catch (err) {
        console.error('Error cargando equipos:', err);
      }
    };

    fetchEquipos();
  }, [token, authLoading]);

  // Cargar template cuando se selecciona un equipo
  useEffect(() => {
    if (!selectedEquipoId) {
      setTemplate(null);
      return;
    }

    const fetchTemplate = async () => {
      setLoading(true);
      setError('');
      setSuccess('');
      
      try {
        const response = await apiClient.get(`v2/checklist-workflow/templates-por-equipo/${selectedEquipoId}/`);
        const templates = response.data.templates || [];
        
        if (templates.length > 0) {
          setTemplate(templates[0]);
          // Inicializar respuestas
          const initialResponses: Record<number, { estado: string; observacion: string }> = {};
          templates[0].categories.forEach((cat: ChecklistCategory) => {
            cat.items.forEach((item: ChecklistItem) => {
              initialResponses[item.id_item] = { estado: '', observacion: '' };
            });
          });
          setResponses(initialResponses);
        } else {
          setError('No se encontró un checklist para este equipo.');
          setTemplate(null);
        }
      } catch (err) {
        console.error('Error cargando template:', err);
        setError('Error al cargar el checklist.');
        setTemplate(null);
      } finally {
        setLoading(false);
      }
    };

    fetchTemplate();
  }, [selectedEquipoId]);

  const handleResponseChange = (itemId: number, field: 'estado' | 'observacion', value: string) => {
    setResponses(prev => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        [field]: value
      }
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!template || !horometro) {
      setError('Complete todos los campos requeridos.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const answers = Object.entries(responses).map(([itemId, data]) => ({
        item: parseInt(itemId),
        estado: data.estado || 'na',
        observacion_item: data.observacion || ''
      }));

      await apiClient.post('v2/checklist-workflow/completar-checklist/', {
        template: template.id_template,
        equipo: parseInt(selectedEquipoId),
        fecha_inspeccion: currentDate,
        horometro_inspeccion: parseInt(horometro),
        lugar_inspeccion: lugar,
        answers: answers,
        imagenes: []
      });

      setSuccess('Checklist enviado exitosamente.');
      setSelectedEquipoId('');
      setTemplate(null);
      setResponses({});
      setHorometro('');
      setLugar('');
    } catch (err: any) {
      console.error('Error enviando checklist:', err);
      setError('Error al enviar el checklist: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
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
        subtitle="Inspección diaria de equipos"
      />

      <div className="max-w-6xl mx-auto space-y-6">
        {/* Selección de equipo */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckSquare className="h-5 w-5" />
              Seleccionar Equipo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Select value={selectedEquipoId} onValueChange={setSelectedEquipoId}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccione un equipo" />
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

        {/* Mensajes */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded-md">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 mr-2" />
              <p>{error}</p>
            </div>
          </div>
        )}

        {success && (
          <div className="bg-green-50 border-l-4 border-green-500 text-green-700 p-4 rounded-md">
            <div className="flex items-center">
              <CheckSquare className="h-5 w-5 mr-2" />
              <p>{success}</p>
            </div>
          </div>
        )}

        {/* Formulario de checklist */}
        {template && (
          <form onSubmit={handleSubmit}>
            <Card>
              <CardHeader>
                <CardTitle>{template.nombre}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Información general */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div>
                    <Label className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      Fecha
                    </Label>
                    <Input type="date" value={currentDate} readOnly className="bg-gray-100" />
                  </div>
                  <div>
                    <Label>Horómetro / Km *</Label>
                    <Input 
                      type="number" 
                      value={horometro} 
                      onChange={(e) => setHorometro(e.target.value)}
                      required 
                    />
                  </div>
                  <div>
                    <Label>Lugar</Label>
                    <Input 
                      type="text" 
                      value={lugar} 
                      onChange={(e) => setLugar(e.target.value)}
                    />
                  </div>
                </div>

                {/* Categorías e items */}
                <div className="space-y-4">
                  {template.categories.sort((a, b) => a.orden - b.orden).map(category => (
                    <Card key={category.id_category}>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-md">{category.nombre}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <table className="w-full">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Ítem</th>
                              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Estado</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Observaciones</th>
                            </tr>
                          </thead>
                          <tbody>
                            {category.items.sort((a, b) => a.orden - b.orden).map(item => (
                              <tr key={item.id_item} className="border-t">
                                <td className="px-4 py-2">
                                  <div className="flex items-center gap-2">
                                    <span>{item.texto}</span>
                                    {item.es_critico && (
                                      <Badge variant="destructive" className="text-xs">Crítico</Badge>
                                    )}
                                  </div>
                                </td>
                                <td className="px-4 py-2">
                                  <div className="flex justify-center gap-2">
                                    {['bueno', 'malo', 'na'].map(estado => (
                                      <label key={estado} className="flex items-center cursor-pointer">
                                        <input
                                          type="radio"
                                          name={`item_${item.id_item}`}
                                          value={estado}
                                          checked={responses[item.id_item]?.estado === estado}
                                          onChange={(e) => handleResponseChange(item.id_item, 'estado', e.target.value)}
                                          className="mr-1"
                                        />
                                        <span className="text-xs">
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
                                    value={responses[item.id_item]?.observacion || ''}
                                    onChange={(e) => handleResponseChange(item.id_item, 'observacion', e.target.value)}
                                    className="text-sm"
                                  />
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* Botón de envío */}
                <div className="flex justify-end">
                  <Button type="submit" disabled={loading} className="flex items-center gap-2">
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Enviando...
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
