// src/services/apiService.ts
// Servicios API centralizados para cada módulo

import apiClient from '../api/apiClient';
import type {
  ApiResponse,
  Equipo,
  TipoEquipo,
  EstadoEquipo,
  Faena,
  PlanMantenimiento,
  DetallePlanMantenimiento,
  TareaEstandar,
  TipoTarea,
  OrdenTrabajo,
  ActividadOrdenTrabajo,
  TipoMantenimientoOT,
  EstadoOrdenTrabajo,
  Agenda,
  ChecklistTemplate,
  ChecklistInstance,
  ChecklistAnswer,
  DashboardStats,
  ChecklistCompletionResponse,
  ChecklistFormData,
  OrdenTrabajoFormData,
  User
} from '../types';

// Servicio base para operaciones CRUD
class BaseService<T> {
  private endpoint: string;

  constructor(endpoint: string) {
    this.endpoint = endpoint;
  }

  async getAll(params?: Record<string, any>): Promise<ApiResponse<T>> {
    const response = await apiClient.get(this.endpoint, { params });
    return response.data;
  }

  async getById(id: number): Promise<T> {
    const response = await apiClient.get(`${this.endpoint}${id}/`);
    return response.data;
  }

  async create(data: Partial<T>): Promise<T> {
    const response = await apiClient.post(this.endpoint, data);
    return response.data;
  }

  async update(id: number, data: Partial<T>): Promise<T> {
    const response = await apiClient.put(`${this.endpoint}${id}/`, data);
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.endpoint}${id}/`);
  }
}

// Servicios específicos para cada módulo
export const equiposService = {
  async getAll(params?: { search?: string; limit?: number }): Promise<any> {
    // Usar datos simulados robustos hasta que la autenticación esté configurada
    console.log('🏗️ [EQUIPOS] Usando datos simulados robustos');
    
    // Generar datos simulados de equipos
    const equiposSimulados = this.generateMockEquipos();
    
    // Aplicar filtros si existen
    let equiposFiltrados = equiposSimulados;
    
    if (params?.search) {
      const searchTerm = params.search.toLowerCase();
      equiposFiltrados = equiposSimulados.filter(equipo => 
        equipo.nombreequipo.toLowerCase().includes(searchTerm) ||
        equipo.codigointerno.toLowerCase().includes(searchTerm) ||
        equipo.patente?.toLowerCase().includes(searchTerm)
      );
    }
    
    if (params?.limit) {
      equiposFiltrados = equiposFiltrados.slice(0, params.limit);
    }
    
    return {
      results: equiposFiltrados,
      count: equiposFiltrados.length,
      total: equiposSimulados.length,
      has_more: equiposFiltrados.length === (params?.limit || 20)
    };
  },

  async getById(id: number): Promise<Equipo> {
    try {
      const response = await apiClient.get(`v2/equipos/${id}/`);
      return response.data;
    } catch (error) {
      console.warn('API V2 de equipos no disponible, usando API V1');
      const response = await apiClient.get(`equipos/${id}/`);
      return response.data;
    }
  },

  async create(data: Partial<Equipo>): Promise<Equipo> {
    try {
      const response = await apiClient.post('v2/equipos/', data);
      return response.data;
    } catch (error) {
      console.warn('API V2 de equipos no disponible, usando API V1');
      const response = await apiClient.post('equipos/', data);
      return response.data;
    }
  },

  async update(id: number, data: Partial<Equipo>): Promise<Equipo> {
    try {
      const response = await apiClient.put(`v2/equipos/${id}/`, data);
      return response.data;
    } catch (error) {
      console.warn('API V2 de equipos no disponible, usando API V1');
      const response = await apiClient.put(`equipos/${id}/`, data);
      return response.data;
    }
  },

  async delete(id: number): Promise<void> {
    try {
      await apiClient.delete(`v2/equipos/${id}/`);
    } catch (error) {
      console.warn('API V2 de equipos no disponible, usando API V1');
      await apiClient.delete(`equipos/${id}/`);
    }
  },
  
  async getList(params?: { search?: string; category?: string; state?: string; limit?: number }): Promise<any> {
    return this.getAll(params);
  },

  async getCategories(): Promise<string[]> {
    // Usar datos simulados
    console.log('📂 [EQUIPOS] Usando categorías simuladas');
    const equipos = this.generateMockEquipos();
    const categorias = [...new Set(equipos.map(e => e.tipo_equipo_nombre))];
    return categorias;
  },

  async getStates(): Promise<string[]> {
    // Usar datos simulados
    console.log('🔧 [EQUIPOS] Usando estados simulados');
    const equipos = this.generateMockEquipos();
    const estados = [...new Set(equipos.map(e => e.estado_nombre))];
    return estados;
  },

  async getStats(): Promise<any> {
    // Usar datos simulados robustos
    console.log('📊 [EQUIPOS] Usando estadísticas simuladas');
    
    // Generar estadísticas basadas en los equipos simulados
    const equipos = this.generateMockEquipos();
    const stats = {
      total_equipos: equipos.length,
      equipos_activos: equipos.filter(e => e.activo).length,
      equipos_inactivos: equipos.filter(e => !e.activo).length,
      equipos_criticos: equipos.filter(e => e.estado_nombre === 'En Mantenimiento').length,
      por_estado: {},
      por_tipo: {},
      por_faena: {}
    };
    
    // Calcular estadísticas por estado
    equipos.forEach(equipo => {
      stats.por_estado[equipo.estado_nombre] = (stats.por_estado[equipo.estado_nombre] || 0) + 1;
      stats.por_tipo[equipo.tipo_equipo_nombre] = (stats.por_tipo[equipo.tipo_equipo_nombre] || 0) + 1;
      stats.por_faena[equipo.faena_nombre] = (stats.por_faena[equipo.faena_nombre] || 0) + 1;
    });
    
    return stats;
  },
  
  async getEquiposCriticos(): Promise<Equipo[]> {
    try {
      const response = await apiClient.get('v2/equipos/criticos/');
      return response.data;
    } catch (error) {
      console.warn('Equipos críticos V2 no disponibles, usando endpoint alternativo');
      const response = await apiClient.get("equipos/", { 
        params: { limit: 10, criticos: 'true' } 
      });
      return response.data.results || [];
    }
  },

  async actualizarHorometro(equipoId: number, horometro: number, observaciones?: string): Promise<void> {
    try {
      await apiClient.put(`v2/equipos/${equipoId}/`, {
        horometro,
        observaciones
      });
    } catch (error) {
      console.warn('API V2 no disponible, usando API V1');
      await apiClient.put(`equipos/${equipoId}/`, {
        horometro,
        observaciones
      });
    }
  },

  // Nuevo método para búsqueda avanzada
  async search(query: string): Promise<any> {
    try {
      const response = await apiClient.get(`v2/search/equipos/?search=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      console.warn('Búsqueda V2 no disponible, usando búsqueda básica');
      const response = await apiClient.get('equipos/', { params: { search: query } });
      return response.data;
    }
  },

  // Función para generar datos simulados de equipos
  generateMockEquipos() {
    const marcas = ['Caterpillar', 'Komatsu', 'Hitachi', 'Volvo', 'JCB', 'Liebherr', 'Case', 'John Deere'];
    const modelos = ['320D', 'EX200', '580SN', 'EC210', 'PC200', 'CX130', 'L150E', '950M', 'PC400'];
    const tipos = ['Excavadora', 'Cargador Frontal', 'Perforadora', 'Bomba', 'Generador', 'Bulldozer', 'Compactador'];
    const estados = ['Activo', 'En Mantenimiento', 'Fuera de Servicio', 'Stand By'];
    const faenas = ['Faena Norte', 'Faena Sur', 'Faena Central', 'Faena Este', 'Faena Oeste'];
    
    const equipos = [];
    
    for (let i = 1; i <= 50; i++) {
      const marca = marcas[Math.floor(Math.random() * marcas.length)];
      const modelo = modelos[Math.floor(Math.random() * modelos.length)];
      const tipo = tipos[Math.floor(Math.random() * tipos.length)];
      const estado = estados[Math.floor(Math.random() * estados.length)];
      const faena = faenas[Math.floor(Math.random() * faenas.length)];
      
      equipos.push({
        idequipo: i,
        codigointerno: `EQ${i.toString().padStart(3, '0')}`,
        nombreequipo: `${marca} ${modelo} ${i}`,
        marca: marca,
        modelo: modelo,
        anio: 2015 + Math.floor(Math.random() * 9),
        patente: `PAT${i.toString().padStart(4, '0')}`,
        tipo_equipo_nombre: tipo,
        estado_nombre: estado,
        faena_nombre: faena,
        activo: estado === 'Activo',
        total_ordenes: Math.floor(Math.random() * 20),
        ordenes_pendientes: Math.floor(Math.random() * 5),
        ultima_mantenimiento: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString()
      });
    }
    
    return equipos;
  }
};

export const tiposEquipoService = new BaseService<TipoEquipo>('tipos-equipo/');
export const estadosEquipoService = new BaseService<EstadoEquipo>('estados-equipo/');
export const faenasService = new BaseService<Faena>('faenas/');

export const planesMantenimientoService = {
  getAll: (params?: Record<string, any>) => new BaseService<PlanMantenimiento>("planes-mantenimiento/").getAll(params),
  getById: (id: number) => new BaseService<PlanMantenimiento>("planes-mantenimiento/").getById(id),
  create: (data: Partial<PlanMantenimiento>) => new BaseService<PlanMantenimiento>("planes-mantenimiento/").create(data),
  update: (id: number, data: Partial<PlanMantenimiento>) => new BaseService<PlanMantenimiento>("planes-mantenimiento/").update(id, data),
  delete: (id: number) => new BaseService<PlanMantenimiento>("planes-mantenimiento/").delete(id),
  
  async generarAgenda(planId: number): Promise<any> {
    const response = await apiClient.get(`planes-mantenimiento/${planId}/generar-agenda/`);
    return response.data;
  },

  async getDetalles(planId: number): Promise<DetallePlanMantenimiento[]> {
    const response = await apiClient.get(`planes-mantenimiento/${planId}/detalles/`);
    return response.data;
  }
};

export const detallesPlanService = new BaseService<DetallePlanMantenimiento>('detalles-plan-mantenimiento/');
export const tareasEstandarService = new BaseService<TareaEstandar>('tareas-estandar/');
export const tiposTareaService = new BaseService<TipoTarea>('tipos-tarea/');

// Función para generar datos simulados de órdenes
const generateMockOrdenes = () => {
  const problemas = [
    'Falla hidráulica en brazo', 'Motor con sobrecalentamiento', 'Problema eléctrico en luces',
    'Fuga de aceite en transmisión', 'Desgaste excesivo de neumáticos', 'Freno de servicio defectuoso',
    'Sistema de dirección con juego', 'Filtro de aire obstruido', 'Batería descargada',
    'Ruido anormal en rodamiento', 'Cuchilla desgastada', 'Cilindro hidráulico con fuga',
    'Correa de transmisión rota', 'Termostato defectuoso', 'Alternador sin carga'
  ];
  
  const prioridades = ['Baja', 'Media', 'Alta', 'Crítica'];
  const estados = ['Pendiente', 'En Proceso', 'Completada', 'Cancelada'];
  const tiposMantenimiento = ['Preventivo', 'Correctivo', 'Modificativo', 'Emergencia'];
  const marcas = ['Caterpillar', 'Komatsu', 'Hitachi', 'Volvo', 'JCB', 'Liebherr', 'Case', 'John Deere'];
  const tecnicos = ['tecnico1', 'tecnico2', 'tecnico3', 'tecnico4', 'tecnico5', 'supervisor1', 'supervisor2'];
  const solicitantes = ['operador1', 'operador2', 'operador3', 'supervisor1', 'supervisor2', 'admin'];
  
  const ordenes = [];
  
  for (let i = 1; i <= 100; i++) {
    const problema = problemas[Math.floor(Math.random() * problemas.length)];
    const prioridad = prioridades[Math.floor(Math.random() * prioridades.length)];
    const estado = estados[Math.floor(Math.random() * estados.length)];
    const tipoMantenimiento = tiposMantenimiento[Math.floor(Math.random() * tiposMantenimiento.length)];
    const marca = marcas[Math.floor(Math.random() * marcas.length)];
    const tecnico = tecnicos[Math.floor(Math.random() * tecnicos.length)];
    const solicitante = solicitantes[Math.floor(Math.random() * solicitantes.length)];
    
    // Fecha aleatoria en los últimos 90 días
    const fechaReporte = new Date();
    fechaReporte.setDate(fechaReporte.getDate() - Math.floor(Math.random() * 90));
    
    const orden = {
      idordentrabajo: i,
      numeroot: `OT-${marca.toUpperCase().substring(0, 3)}${i.toString().padStart(4, '0')}`,
      descripcionproblemareportado: problema,
      prioridad: prioridad,
      estado_nombre: estado,
      tipo_mantenimiento_nombre: tipoMantenimiento,
      equipo_nombre: `${marca} ${i}`,
      tecnico_nombre: tecnico,
      solicitante_nombre: solicitante,
      fechareportefalla: fechaReporte.toISOString(),
      fechaejecucion: estado === 'En Proceso' || estado === 'Completada' ? 
        new Date(fechaReporte.getTime() + Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString() : null,
      fechacompletado: estado === 'Completada' ? 
        new Date(fechaReporte.getTime() + Math.random() * 14 * 24 * 60 * 60 * 1000).toISOString() : null,
      tiempototalminutos: estado === 'Completada' ? Math.floor(Math.random() * 480) + 60 : null,
      observacionesfinales: estado === 'Completada' ? `Orden ${i} completada exitosamente` : null,
      horometro: Math.floor(Math.random() * 10000) + 1000
    };
    
    ordenes.push(orden);
  }
  
  // Ordenar por fecha de reporte (más recientes primero)
  return ordenes.sort((a, b) => new Date(b.fechareportefalla).getTime() - new Date(a.fechareportefalla).getTime());
};

export const ordenesTrabajoService = {
  async getAll(params?: { search?: string; status?: string; priority?: string; limit?: number }): Promise<any> {
    // Usar datos simulados robustos hasta que la autenticación esté configurada
    console.log('📋 [ORDENES] Usando datos simulados robustos');
    
    // Generar datos simulados de órdenes
    const ordenesSimuladas = generateMockOrdenes();
    
    // Aplicar filtros si existen
    let ordenesFiltradas = ordenesSimuladas;
    
    if (params?.search) {
      const searchTerm = params.search.toLowerCase();
      ordenesFiltradas = ordenesFiltradas.filter(orden => 
        orden.numeroot.toLowerCase().includes(searchTerm) ||
        orden.descripcionproblemareportado.toLowerCase().includes(searchTerm) ||
        orden.equipo_nombre.toLowerCase().includes(searchTerm)
      );
    }
    
    if (params?.status && params.status !== 'all') {
      ordenesFiltradas = ordenesFiltradas.filter(orden => 
        orden.estado_nombre === params.status
      );
    }
    
    if (params?.priority && params.priority !== 'all') {
      ordenesFiltradas = ordenesFiltradas.filter(orden => 
        orden.prioridad === params.priority
      );
    }
    
    if (params?.limit) {
      ordenesFiltradas = ordenesFiltradas.slice(0, params.limit);
    }
    
    return {
      results: ordenesFiltradas,
      count: ordenesFiltradas.length,
      total: ordenesSimuladas.length,
      has_more: ordenesFiltradas.length === (params?.limit || 20)
    };
  },

  async getById(id: number): Promise<OrdenTrabajo> {
    try {
      const response = await apiClient.get(`v2/ordenes-trabajo/${id}/`);
      return response.data;
    } catch (error) {
      console.warn('API V2 de órdenes no disponible, usando API V1');
      const response = await apiClient.get(`ordenes-trabajo/${id}/`);
      return response.data;
    }
  },

  async create(data: Partial<OrdenTrabajo>): Promise<OrdenTrabajo> {
    try {
      const response = await apiClient.post('v2/ordenes-trabajo/', data);
      return response.data;
    } catch (error) {
      console.warn('API V2 de órdenes no disponible, usando API V1');
      const response = await apiClient.post('ordenes-trabajo/', data);
      return response.data;
    }
  },

  async update(id: number, data: Partial<OrdenTrabajo>): Promise<OrdenTrabajo> {
    try {
      const response = await apiClient.put(`v2/ordenes-trabajo/${id}/`, data);
      return response.data;
    } catch (error) {
      console.warn('API V2 de órdenes no disponible, usando API V1');
      const response = await apiClient.put(`ordenes-trabajo/${id}/`, data);
      return response.data;
    }
  },

  async delete(id: number): Promise<void> {
    try {
      await apiClient.delete(`v2/ordenes-trabajo/${id}/`);
    } catch (error) {
      console.warn('API V2 de órdenes no disponible, usando API V1');
      await apiClient.delete(`ordenes-trabajo/${id}/`);
    }
  },
  
  async getList(params?: { search?: string; status?: string; priority?: string; type?: string; limit?: number }): Promise<any> {
    return this.getAll(params);
  },

  async getStats(): Promise<any> {
    // Usar datos simulados robustos
    console.log('📊 [ORDENES] Usando estadísticas simuladas');
    
    // Generar estadísticas basadas en los órdenes simulados
    const ordenes = generateMockOrdenes();
    const stats = {
      total_ordenes: ordenes.length,
      pendientes: ordenes.filter(o => o.estado_nombre === 'Pendiente').length,
      en_proceso: ordenes.filter(o => o.estado_nombre === 'En Proceso').length,
      completadas: ordenes.filter(o => o.estado_nombre === 'Completada').length,
      canceladas: ordenes.filter(o => o.estado_nombre === 'Cancelada').length,
      por_estado: {},
      por_prioridad: {},
      por_tipo_mantenimiento: {}
    };
    
    // Calcular estadísticas por estado, prioridad y tipo
    ordenes.forEach(orden => {
      stats.por_estado[orden.estado_nombre] = (stats.por_estado[orden.estado_nombre] || 0) + 1;
      stats.por_prioridad[orden.prioridad] = (stats.por_prioridad[orden.prioridad] || 0) + 1;
      stats.por_tipo_mantenimiento[orden.tipo_mantenimiento_nombre] = (stats.por_tipo_mantenimiento[orden.tipo_mantenimiento_nombre] || 0) + 1;
    });
    
    return stats;
  },

  async getFilters(): Promise<any> {
    // Usar datos simulados robustos
    console.log('🔍 [ORDENES] Usando filtros simulados');
    return {
      statuses: ['Pendiente', 'En Proceso', 'Completada', 'Cancelada'],
      priorities: ['Baja', 'Media', 'Alta', 'Crítica'],
      types: ['Preventivo', 'Correctivo', 'Modificativo', 'Emergencia']
    };
  },

  async getByEquipment(equipmentId: number): Promise<OrdenTrabajo[]> {
    try {
      const response = await apiClient.get('v2/ordenes-trabajo/', { 
        params: { idequipo: equipmentId } 
      });
      return response.data.results || [];
    } catch (error) {
      console.warn('API V2 no disponible, usando API V1');
      const response = await apiClient.get('ordenes-trabajo/', { 
        params: { equipment: equipmentId } 
      });
      return response.data.results || [];
    }
  },
  
  async crearDesdeplan(data: OrdenTrabajoFormData): Promise<OrdenTrabajo> {
    return this.create(data);
  },

  async reportarFalla(data: {
    idequipo: number;
    idsolicitante: number;
    descripcionproblemareportado: string;
    prioridad: string;
  }): Promise<OrdenTrabajo> {
    return this.create(data);
  },

  // Nuevos métodos V2
  async getRecientes(limit: number = 10): Promise<OrdenTrabajo[]> {
    try {
      const response = await apiClient.get(`v2/ordenes-trabajo/recientes/?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.warn('Órdenes recientes V2 no disponibles, usando endpoint alternativo');
      const response = await apiClient.get('ordenes-trabajo/', { params: { limit } });
      return response.data.results || [];
    }
  },

  async getVencidas(): Promise<OrdenTrabajo[]> {
    try {
      const response = await apiClient.get('v2/ordenes-trabajo/vencidas/');
      return response.data;
    } catch (error) {
      console.warn('Órdenes vencidas V2 no disponibles, usando filtro alternativo');
      const response = await apiClient.get('ordenes-trabajo/', { 
        params: { dias_pendientes: 7 } 
      });
      return response.data.results || [];
    }
  },

  async search(query: string): Promise<any> {
    try {
      const response = await apiClient.get(`v2/search/ordenes/?search=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      console.warn('Búsqueda V2 no disponible, usando búsqueda básica');
      const response = await apiClient.get('ordenes-trabajo/', { params: { search: query } });
      return response.data;
    }
  }
};

export const actividadesOTService = {
  getAll: (params?: Record<string, any>) => new BaseService<ActividadOrdenTrabajo>("actividades-ot/").getAll(params),
  getById: (id: number) => new BaseService<ActividadOrdenTrabajo>("actividades-ot/").getById(id),
  create: (data: Partial<ActividadOrdenTrabajo>) => new BaseService<ActividadOrdenTrabajo>("actividades-ot/").create(data),
  update: (id: number, data: Partial<ActividadOrdenTrabajo>) => new BaseService<ActividadOrdenTrabajo>("actividades-ot/").update(id, data),
  delete: (id: number) => new BaseService<ActividadOrdenTrabajo>("actividades-ot/").delete(id),
  
  async completarActividad(actividadId: number, data: {
    observaciones?: string;
    tiempo_real_minutos?: number;
    resultado_inspeccion?: string;
    medicion_valor?: number;
    unidad_medicion?: string;
  }): Promise<ActividadOrdenTrabajo> {
    const response = await apiClient.post("mantenimiento-workflow/completar-actividad/", {
      actividad_id: actividadId,
      ...data
    });
    return response.data;
  }
};

export const tiposMantenimientoOTService = new BaseService<TipoMantenimientoOT>('tipos-mantenimiento-ot/');
export const estadosOrdenTrabajoService = new BaseService<EstadoOrdenTrabajo>('estados-orden-trabajo/');

export const agendaService = {
  getAll: (params?: Record<string, any>) => new BaseService<Agenda>("agendas/").getAll(params),
  getById: (id: number) => new BaseService<Agenda>("agendas/").getById(id),
  create: (data: Partial<Agenda>) => new BaseService<Agenda>("agendas/").create(data),
  update: (id: number, data: Partial<Agenda>) => new BaseService<Agenda>("agendas/").update(id, data),
  delete: (id: number) => new BaseService<Agenda>("agendas/").delete(id),
  
  async getCalendario(start: string, end: string): Promise<Agenda[]> {
    const response = await apiClient.get(`agendas/calendario/?start=${start}&end=${end}`);
    return response.data;
  }
};

export const checklistService = {
  templates: new BaseService<ChecklistTemplate>('checklist-templates/'),
  instances: new BaseService<ChecklistInstance>('checklist-instances/'),
  answers: new BaseService<ChecklistAnswer>('checklist-answers/'),
  
  async getTemplatesPorEquipo(equipoId: number): Promise<ChecklistTemplate[]> {
    const response = await apiClient.get(`checklist-workflow/templates-por-equipo/${equipoId}/`);
    return response.data;
  },

  async completarChecklist(data: ChecklistFormData): Promise<ChecklistCompletionResponse> {
    const response = await apiClient.post('checklist-workflow/completar-checklist/', data);
    return response.data;
  },

  async getHistorialEquipo(equipoId: number, fechaInicio?: string, fechaFin?: string): Promise<ChecklistInstance[]> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await apiClient.get(`checklist-workflow/historial-equipo/${equipoId}/?${params}`);
    return response.data;
  },

  async getReporteConformidad(fechaInicio?: string, fechaFin?: string): Promise<any> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await apiClient.get(`checklist-workflow/reportes/conformidad/?${params}`);
    return response.data;
  },

  async getElementosMasFallidos(fechaInicio?: string, fechaFin?: string): Promise<any> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await apiClient.get(`checklist-workflow/elementos-mas-fallidos/?${params}`);
    return response.data;
  }
};

export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    try {
      const response = await apiClient.get('v2/dashboard/stats/');
      console.log('📊 [DASHBOARD] Stats cargadas desde el backend:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ [DASHBOARD] Error cargando stats desde el backend:', error);
      throw error;
    }
  },

  async getRecentWorkOrders(): Promise<OrdenTrabajo[]> {
    try {
      const response = await apiClient.get('v2/dashboard/recent_work_orders/');
      console.log('📋 [DASHBOARD] Órdenes recientes cargadas desde el backend:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ [DASHBOARD] Error cargando órdenes recientes:', error);
      throw error;
    }
  },

  async getMonthlyData(): Promise<any[]> {
    try {
      const response = await apiClient.get('v2/dashboard/monthly_data/');
      console.log('📅 [DASHBOARD] Datos mensuales cargados desde el backend:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ [DASHBOARD] Error cargando datos mensuales:', error);
      throw error;
    }
  },

  async getMaintenanceTypes(): Promise<any[]> {
    try {
      const response = await apiClient.get('v2/dashboard/maintenance_types/');
      console.log('🔧 [DASHBOARD] Tipos de mantenimiento cargados desde el backend:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ [DASHBOARD] Error cargando tipos de mantenimiento:', error);
      throw error;
    }
  },

  async getReporteEficiencia(fechaInicio?: string, fechaFin?: string): Promise<any> {
    // Usar datos reales de las APIs V2
    try {
      const [stats, monthlyData] = await Promise.all([
        this.getStats(),
        this.getMonthlyData()
      ]);
      
      return {
        eficiencia_general: stats.sistema.eficiencia,
        tiempo_promedio_resolucion: `${stats.ordenes.tiempo_promedio_horas} horas`,
        equipos_mas_problematicos: [
          { equipo: 'Equipos en Mantenimiento', fallas: stats.equipos.en_mantenimiento },
          { equipo: 'Órdenes Vencidas', fallas: stats.ordenes.vencidas }
        ],
        tendencia_mensual: monthlyData.slice(-6) // Últimos 6 meses
      };
    } catch (error) {
      console.warn('Reporte de eficiencia no disponible, usando datos simulados');
      return {
        eficiencia_general: 87.2,
        tiempo_promedio_resolucion: '24.5 horas',
        equipos_mas_problematicos: [
          { equipo: 'Equipo A', fallas: 5 },
          { equipo: 'Equipo B', fallas: 3 }
        ]
      };
    }
  },

};

export const authService = {
  async login(username: string, password: string): Promise<{ token: string; user: User }> {
    const response = await apiClient.post('login/', { username, password });
    return response.data;
  },

  async logout(): Promise<void> {
    await apiClient.post('logout/');
  }
};

// Servicio para usuarios
export const userService = new BaseService<User>("users/");

