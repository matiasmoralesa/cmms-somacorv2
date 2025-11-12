import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageLayout, PageHeader } from '@/components/layout/PageLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, Save, AlertTriangle } from 'lucide-react';
import { equiposService } from '@/services/apiService';
import apiClient from '@/api/apiClient';

interface EquipoForm {
  codigointerno: string;
  nombreequipo: string;
  marca: string;
  modelo: string;
  patente: string;
  idtipoequipo: number | null;
  idfaenaactual: number | null;
  idestadoactual: number | null;
  anio: number | null;
  activo: boolean;
}

export default function EquipoEditarView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tiposEquipo, setTiposEquipo] = useState<any[]>([]);
  const [faenas, setFaenas] = useState<any[]>([]);
  const [estados, setEstados] = useState<any[]>([]);
  
  const [formData, setFormData] = useState<EquipoForm>({
    codigointerno: '',
    nombreequipo: '',
    marca: '',
    modelo: '',
    patente: '',
    idtipoequipo: null,
    idfaenaactual: null,
    idestadoactual: null,
    anio: null,
    activo: true
  });

  useEffect(() => {
    if (id) {
      loadEquipoData();
      loadCatalogos();
    }
  }, [id]);

  const loadCatalogos = async () => {
    try {
      console.log('🔄 Cargando catálogos...');
      
      // Cargar tipos de equipo
      const tiposResponse = await apiClient.get('v2/tipos-equipo/');
      const tiposData = tiposResponse.data.results || tiposResponse.data || [];
      console.log('📦 Tipos de equipo cargados:', tiposData.length, tiposData);
      setTiposEquipo(tiposData);

      // Cargar faenas
      const faenasResponse = await apiClient.get('v2/faenas/');
      const faenasData = faenasResponse.data.results || faenasResponse.data || [];
      console.log('📍 Faenas cargadas:', faenasData.length, faenasData);
      setFaenas(faenasData);

      // Cargar estados - usando el endpoint de equipos para obtener los estados únicos
      const equiposResponse = await apiClient.get('v2/equipos/');
      const equipos = equiposResponse.data.results || [];
      console.log('🚜 Equipos para extraer estados:', equipos.length);
      
      // Extraer estados únicos de los equipos
      const estadosUnicos = new Map();
      equipos.forEach((equipo: any) => {
        if (equipo.idestadoactual && equipo.estado_nombre) {
          estadosUnicos.set(equipo.idestadoactual, {
            idestadoequipo: equipo.idestadoactual,
            nombreestado: equipo.estado_nombre
          });
        }
      });
      
      const estadosData = Array.from(estadosUnicos.values());
      console.log('📊 Estados extraídos:', estadosData.length, estadosData);
      setEstados(estadosData);
      
      console.log('✅ Catálogos cargados exitosamente');
    } catch (err) {
      console.error('❌ Error loading catalogos:', err);
    }
  };

  const loadEquipoData = async () => {
    try {
      setLoading(true);
      const equipoData = await equiposService.getById(Number(id));
      
      setFormData({
        codigointerno: equipoData.codigointerno || '',
        nombreequipo: equipoData.nombreequipo || '',
        marca: equipoData.marca || '',
        modelo: equipoData.modelo || '',
        patente: equipoData.patente || '',
        idtipoequipo: equipoData.idtipoequipo || null,
        idfaenaactual: equipoData.idfaenaactual || null,
        idestadoactual: equipoData.idestadoactual || null,
        anio: equipoData.anio || null,
        activo: equipoData.activo !== undefined ? equipoData.activo : true
      });
    } catch (err) {
      console.error('Error loading equipo:', err);
      setError('Error al cargar los datos del equipo');
    } finally {
      setLoading(false);
    }
  };



  const handleInputChange = (field: keyof EquipoForm, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setError(null);

      await equiposService.update(Number(id), formData);
      
      navigate(`/equipos/${id}`);
    } catch (err: any) {
      console.error('Error updating equipo:', err);
      setError(err.response?.data?.message || 'Error al actualizar el equipo');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Cargando datos del equipo...</p>
          </div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader
        title="Editar Equipo"
        description={`Modificar información del equipo ${formData.nombreequipo}`}
        action={
          <Button variant="outline" onClick={() => navigate(`/equipos/${id}`)}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Cancelar
          </Button>
        }
      />

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-800">
              <AlertTriangle className="h-5 w-5" />
              <p>{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Información del Equipo</CardTitle>
            <CardDescription>Actualiza los datos del equipo</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Código Interno */}
              <div className="space-y-2">
                <Label htmlFor="codigointerno">Código Interno *</Label>
                <Input
                  id="codigointerno"
                  value={formData.codigointerno}
                  onChange={(e) => handleInputChange('codigointerno', e.target.value)}
                  required
                />
              </div>

              {/* Nombre */}
              <div className="space-y-2">
                <Label htmlFor="nombreequipo">Nombre del Equipo *</Label>
                <Input
                  id="nombreequipo"
                  value={formData.nombreequipo}
                  onChange={(e) => handleInputChange('nombreequipo', e.target.value)}
                  required
                />
              </div>

              {/* Marca */}
              <div className="space-y-2">
                <Label htmlFor="marca">Marca</Label>
                <Input
                  id="marca"
                  value={formData.marca}
                  onChange={(e) => handleInputChange('marca', e.target.value)}
                />
              </div>

              {/* Modelo */}
              <div className="space-y-2">
                <Label htmlFor="modelo">Modelo</Label>
                <Input
                  id="modelo"
                  value={formData.modelo}
                  onChange={(e) => handleInputChange('modelo', e.target.value)}
                />
              </div>

              {/* Patente */}
              <div className="space-y-2">
                <Label htmlFor="patente">Patente</Label>
                <Input
                  id="patente"
                  value={formData.patente}
                  onChange={(e) => handleInputChange('patente', e.target.value)}
                />
              </div>

              {/* Tipo de Equipo */}
              <div className="space-y-2">
                <Label htmlFor="idtipoequipo">Tipo de Equipo *</Label>
                <Select
                  value={formData.idtipoequipo?.toString() || ''}
                  onValueChange={(value) => handleInputChange('idtipoequipo', Number(value))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    {tiposEquipo.map((tipo) => (
                      <SelectItem key={tipo.idtipoequipo} value={tipo.idtipoequipo.toString()}>
                        {tipo.nombretipo}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Faena */}
              <div className="space-y-2">
                <Label htmlFor="idfaenaactual">Faena / Ubicación</Label>
                <Select
                  value={formData.idfaenaactual?.toString() || ''}
                  onValueChange={(value) => handleInputChange('idfaenaactual', Number(value))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar faena" />
                  </SelectTrigger>
                  <SelectContent>
                    {faenas.map((faena) => (
                      <SelectItem key={faena.idfaena} value={faena.idfaena.toString()}>
                        {faena.nombrefaena}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Estado */}
              <div className="space-y-2">
                <Label htmlFor="idestadoactual">Estado *</Label>
                <Select
                  value={formData.idestadoactual?.toString() || ''}
                  onValueChange={(value) => handleInputChange('idestadoactual', Number(value))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar estado" />
                  </SelectTrigger>
                  <SelectContent>
                    {estados.map((estado) => (
                      <SelectItem key={estado.idestadoequipo} value={estado.idestadoequipo.toString()}>
                        {estado.nombreestado}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Año Fabricación */}
              <div className="space-y-2">
                <Label htmlFor="anio">Año de Fabricación</Label>
                <Input
                  id="anio"
                  type="number"
                  value={formData.anio || ''}
                  onChange={(e) => handleInputChange('anio', e.target.value ? Number(e.target.value) : null)}
                  placeholder="2020"
                  min="1900"
                  max={new Date().getFullYear() + 1}
                />
              </div>

              {/* Estado Activo */}
              <div className="space-y-2">
                <Label htmlFor="activo">Estado</Label>
                <Select
                  value={formData.activo ? 'true' : 'false'}
                  onValueChange={(value) => handleInputChange('activo', value === 'true')}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="true">Activo</SelectItem>
                    <SelectItem value="false">Inactivo</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-6 border-t">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate(`/equipos/${id}`)}
                disabled={saving}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={saving}>
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Guardando...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Guardar Cambios
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </PageLayout>
  );
}
