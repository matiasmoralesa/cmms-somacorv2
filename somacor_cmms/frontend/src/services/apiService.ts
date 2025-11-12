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
    try {
      const response = await apiClient.get('v2/equipos/', { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener equipos:', error);
      throw error;
    }
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
    try {
      const response = await apiClient.get('v2/tipos-equipo/');
      const results = Array.isArray(response.data.results) ? response.data.results : [];
      return results.map((t: any) => t.nombretipo || t.nombre).filter(Boolean);
    } catch (error) {
      console.error('Error al obtener categorías:', error);
      return [];
    }
  },

  async getStates(): Promise<string[]> {
    try {
      const response = await apiClient.get('v2/equipos/');
      const equipos = Array.isArray(response.data.results) ? response.data.results : [];
      const estados = [...new Set(equipos.map((e: any) => e.estado_nombre).filter(Boolean))];
      return estados;
    } catch (error) {
      console.error('Error al obtener estados:', error);
      return [];
    }
  },

  async getStats(): Promise<any> {
    try {
      const response = await apiClient.get('v2/equipos/');
      const equipos = Array.isArray(response.data.results) ? response.data.results : [];
      
      const stats = {
        total_equipos: response.data.count || equipos.length,
        equipos_activos: equipos.filter((e: any) => e.activo).length,
        equipos_inactivos: equipos.filter((e: any) => !e.activo).length,
        equipos_en_mantenimiento: equipos.filter((e: any) => e.estado_nombre && e.estado_nombre.toLowerCase().includes('mantenimiento')).length,
        equipos_criticos: equipos.filter((e: any) => e.estado_nombre === 'En Mantenimiento').length,
        por_estado: {} as Record<string, number>,
        por_tipo: {} as Record<string, number>,
        por_faena: {} as Record<string, number>
      };
      
      equipos.forEach((equipo: any) => {
        if (equipo.estado_nombre) {
          stats.por_estado[equipo.estado_nombre] = (stats.por_estado[equipo.estado_nombre] || 0) + 1;
        }
        if (equipo.tipo_equipo_nombre) {
          stats.por_tipo[equipo.tipo_equipo_nombre] = (stats.por_tipo[equipo.tipo_equipo_nombre] || 0) + 1;
        }
        if (equipo.faena_nombre) {
          stats.por_faena[equipo.faena_nombre] = (stats.por_faena[equipo.faena_nombre] || 0) + 1;
        }
      });
      
      return stats;
    } catch (error) {
      console.error('Error al obtener estadísticas:', error);
      return {
        total_equipos: 0,
        equipos_activos: 0,
        equipos_inactivos: 0,
        equipos_en_mantenimiento: 0,
        equipos_criticos: 0,
        por_estado: {},
        por_tipo: {},
        por_faena: {}
      };
    }
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
    try {
      const response = await apiClient.get('v2/ordenes-trabajo/', { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener órdenes de trabajo:', error);
      throw error;
    }
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
    try {
      const response = await apiClient.get('v2/ordenes-trabajo/');
      const ordenes = response.data.results;
      
      const stats = {
        total_ordenes: response.data.count,
        pendientes: ordenes.filter((o: any) => o.estado_nombre === 'Pendiente').length,
        en_proceso: ordenes.filter((o: any) => o.estado_nombre === 'En Proceso').length,
        completadas: ordenes.filter((o: any) => o.estado_nombre === 'Completada').length,
        canceladas: ordenes.filter((o: any) => o.estado_nombre === 'Cancelada').length,
        por_estado: {} as Record<string, number>,
        por_prioridad: {} as Record<string, number>,
        por_tipo_mantenimiento: {} as Record<string, number>
      };
      
      ordenes.forEach((orden: any) => {
        stats.por_estado[orden.estado_nombre] = (stats.por_estado[orden.estado_nombre] || 0) + 1;
        stats.por_prioridad[orden.prioridad] = (stats.por_prioridad[orden.prioridad] || 0) + 1;
      });
      
      return stats;
    } catch (error) {
      console.error('Error al obtener estadísticas de órdenes:', error);
      return {
        total_ordenes: 0,
        pendientes: 0,
        en_proceso: 0,
        completadas: 0,
        canceladas: 0,
        por_estado: {},
        por_prioridad: {},
        por_tipo_mantenimiento: {}
      };
    }
  },

  async getFilters(): Promise<any> {
    try {
      const response = await apiClient.get('v2/ordenes-trabajo/');
      const ordenes = response.data.results;
      
      const statuses = [...new Set(ordenes.map((o: any) => o.estado_nombre))];
      const priorities = [...new Set(ordenes.map((o: any) => o.prioridad))];
      
      return {
        statuses,
        priorities,
        types: ['Preventivo', 'Correctivo', 'Modificativo', 'Emergencia']
      };
    } catch (error) {
      console.error('Error al obtener filtros:', error);
      return {
        statuses: [],
        priorities: [],
        types: []
      };
    }
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
    const response = await apiClient.get(`v2/checklist-workflow/templates-por-equipo/${equipoId}/`);
    return response.data;
  },

  async completarChecklist(data: ChecklistFormData): Promise<ChecklistCompletionResponse> {
    const response = await apiClient.post('v2/checklist-workflow/completar-checklist/', data);
    return response.data;
  },

  async getHistorialEquipo(equipoId: number, fechaInicio?: string, fechaFin?: string): Promise<ChecklistInstance[]> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await apiClient.get(`v2/checklist-workflow/historial-equipo/${equipoId}/?${params}`);
    return response.data;
  },

  async getReporteConformidad(fechaInicio?: string, fechaFin?: string): Promise<any> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await apiClient.get(`v2/checklist-workflow/reportes/conformidad/?${params}`);
    return response.data;
  },

  async getElementosMasFallidos(fechaInicio?: string, fechaFin?: string): Promise<any> {
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    const response = await apiClient.get(`v2/checklist-workflow/elementos-mas-fallidos/?${params}`);
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
      const response = await apiClient.get('v2/dashboard/recent_work_orders/', {
        params: { limit: 5 }
      });
      console.log('📋 [DASHBOARD] Órdenes recientes cargadas desde el backend:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ [DASHBOARD] Error cargando órdenes recientes:', error);
      // Retornar array vacío en caso de error
      return [];
    }
  },

  async getMonthlyData(): Promise<any[]> {
    try {
      // No pasar parámetro year para obtener los últimos 12 meses automáticamente
      // Si necesitas un año específico, puedes pasar: params: { year: 2024 }
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
      // Retornar datos por defecto
      return [
        { tipo: 'Preventivo', cantidad: 45 },
        { tipo: 'Correctivo', cantidad: 30 },
        { tipo: 'Predictivo', cantidad: 15 },
        { tipo: 'Emergencia', cantidad: 10 }
      ];
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

