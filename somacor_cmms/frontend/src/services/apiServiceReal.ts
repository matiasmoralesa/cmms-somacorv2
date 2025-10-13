// src/services/apiServiceReal.ts
// Servicios API que se conectan al backend REAL (sin datos simulados)

import apiClient from '../api/apiClient';

// =================================================================================
// TIPOS DE DATOS
// =================================================================================

interface ApiResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}

interface Equipo {
  idequipo: number;
  codigointerno: string;
  nombreequipo: string;
  marca?: string;
  modelo?: string;
  anio?: number;
  patente?: string;
  tipo_equipo_nombre?: string;
  estado_nombre?: string;
  faena_nombre?: string;
  activo: boolean;
}

interface TipoEquipo {
  idtipoequipo: number;
  nombretipo: string;
  descripcion?: string;
  activo: boolean;
}

interface EstadoEquipo {
  idestadoequipo: number;
  nombreestado: string;
  descripcion?: string;
}

interface Faena {
  idfaena: number;
  nombrefaena: string;
  descripcion?: string;
  activa: boolean;
}

interface TipoMantenimientoOT {
  idtipomantenimientoot: number;
  nombretipo: string;
  descripcion?: string;
}

interface EstadoOrdenTrabajo {
  idestadoot: number;
  nombreestadoot: string;
  descripcion?: string;
}

interface Usuario {
  idusuario: number;
  nombres: string;
  apellidos: string;
  correoelectronico: string;
  telefonocontacto?: string;
  activo: boolean;
  idrol?: number;
  rol_nombre?: string;
}

interface Rol {
  idrol: number;
  nombrerol: string;
  descripcion?: string;
}

// =================================================================================
// SERVICIOS DE EQUIPOS
// =================================================================================

export const equiposServiceReal = {
  async getAll(params?: { search?: string; limit?: number }): Promise<ApiResponse<Equipo>> {
    try {
      console.log('[EQUIPOS] Conectando al backend real...');
      const response = await apiClient.get('v2/equipos/', { params });
      console.log('[EQUIPOS] Datos recibidos del backend:', response.data);
      return response.data;
    } catch (error) {
      console.error('[EQUIPOS] Error conectando al backend:', error);
      throw error;
    }
  },

  async getById(id: number): Promise<Equipo> {
    try {
      const response = await apiClient.get(`v2/equipos/${id}/`);
      return response.data;
    } catch (error) {
      console.error('[EQUIPOS] Error obteniendo equipo:', error);
      throw error;
    }
  },

  async create(data: Partial<Equipo>): Promise<Equipo> {
    try {
      const response = await apiClient.post('v2/equipos/', data);
      return response.data;
    } catch (error) {
      console.error('[EQUIPOS] Error creando equipo:', error);
      throw error;
    }
  },

  async update(id: number, data: Partial<Equipo>): Promise<Equipo> {
    try {
      const response = await apiClient.put(`v2/equipos/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error('[EQUIPOS] Error actualizando equipo:', error);
      throw error;
    }
  },

  async delete(id: number): Promise<void> {
    try {
      await apiClient.delete(`v2/equipos/${id}/`);
    } catch (error) {
      console.error('[EQUIPOS] Error eliminando equipo:', error);
      throw error;
    }
  }
};

// =================================================================================
// SERVICIOS DE TIPOS DE EQUIPO
// =================================================================================

export const tiposEquipoServiceReal = {
  async getAll(params?: Record<string, any>): Promise<ApiResponse<TipoEquipo>> {
    try {
      console.log('[TIPOS EQUIPO] Conectando al backend real...');
      const response = await apiClient.get('v2/tipos-equipo/', { params });
      console.log('[TIPOS EQUIPO] Datos recibidos:', response.data);
      return response.data;
    } catch (error) {
      console.error('[TIPOS EQUIPO] Error:', error);
      throw error;
    }
  },

  async getById(id: number): Promise<TipoEquipo> {
    try {
      const response = await apiClient.get(`v2/tipos-equipo/${id}/`);
      return response.data;
    } catch (error) {
      console.error('[TIPOS EQUIPO] Error:', error);
      throw error;
    }
  }
};

// =================================================================================
// SERVICIOS DE ESTADOS DE EQUIPO
// =================================================================================

export const estadosEquipoServiceReal = {
  async getAll(params?: Record<string, any>): Promise<ApiResponse<EstadoEquipo>> {
    try {
      console.log('[ESTADOS EQUIPO] Conectando al backend real...');
      const response = await apiClient.get('estados-equipo/', { params });
      console.log('[ESTADOS EQUIPO] Datos recibidos:', response.data);
      return response.data;
    } catch (error) {
      console.error('[ESTADOS EQUIPO] Error:', error);
      throw error;
    }
  },

  async getById(id: number): Promise<EstadoEquipo> {
    try {
      const response = await apiClient.get(`estados-equipo/${id}/`);
      return response.data;
    } catch (error) {
      console.error('[ESTADOS EQUIPO] Error:', error);
      throw error;
    }
  }
};

// =================================================================================
// SERVICIOS DE FAENAS
// =================================================================================

export const faenasServiceReal = {
  async getAll(params?: Record<string, any>): Promise<ApiResponse<Faena>> {
    try {
      console.log('[FAENAS] Conectando al backend real...');
      const response = await apiClient.get('v2/faenas/', { params });
      console.log('[FAENAS] Datos recibidos:', response.data);
      return response.data;
    } catch (error) {
      console.error('[FAENAS] Error:', error);
      throw error;
    }
  },

  async getById(id: number): Promise<Faena> {
    try {
      const response = await apiClient.get(`v2/faenas/${id}/`);
      return response.data;
    } catch (error) {
      console.error('[FAENAS] Error:', error);
      throw error;
    }
  }
};

// =================================================================================
// SERVICIOS DE ÓRDENES DE TRABAJO
// =================================================================================

export const ordenesTrabajoServiceReal = {
  async getAll(params?: { search?: string; status?: string; priority?: string; limit?: number }): Promise<ApiResponse<any>> {
    try {
      console.log('[ORDENES] Conectando al backend real...');
      const response = await apiClient.get('v2/ordenes-trabajo/', { params });
      console.log('[ORDENES] Datos recibidos:', response.data);
      return response.data;
    } catch (error) {
      console.error('[ORDENES] Error:', error);
      throw error;
    }
  },

  async getById(id: number): Promise<any> {
    try {
      const response = await apiClient.get(`v2/ordenes-trabajo/${id}/`);
      return response.data;
    } catch (error) {
      console.error('[ORDENES] Error:', error);
      throw error;
    }
  },

  async create(data: Partial<any>): Promise<any> {
    try {
      console.log('[ORDENES] Creando orden de trabajo:', data);
      const response = await apiClient.post('v2/ordenes-trabajo/', data);
      console.log('[ORDENES] Orden creada:', response.data);
      return response.data;
    } catch (error) {
      console.error('[ORDENES] Error creando orden:', error);
      throw error;
    }
  },

  async update(id: number, data: Partial<any>): Promise<any> {
    try {
      const response = await apiClient.put(`v2/ordenes-trabajo/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error('[ORDENES] Error:', error);
      throw error;
    }
  },

  async delete(id: number): Promise<void> {
    try {
      await apiClient.delete(`v2/ordenes-trabajo/${id}/`);
    } catch (error) {
      console.error('[ORDENES] Error:', error);
      throw error;
    }
  }
};

// =================================================================================
// SERVICIOS DE TIPOS DE MANTENIMIENTO
// =================================================================================

export const tiposMantenimientoOTServiceReal = {
  async getAll(params?: Record<string, any>): Promise<ApiResponse<TipoMantenimientoOT>> {
    try {
      console.log('[TIPOS MANTENIMIENTO] Conectando al backend real...');
      const response = await apiClient.get('tipos-mantenimiento-ot/', { params });
      console.log('[TIPOS MANTENIMIENTO] Datos recibidos:', response.data);
      return response.data;
    } catch (error) {
      console.error('[TIPOS MANTENIMIENTO] Error:', error);
      throw error;
    }
  },

  async getById(id: number): Promise<TipoMantenimientoOT> {
    try {
      const response = await apiClient.get(`tipos-mantenimiento-ot/${id}/`);
      return response.data;
    } catch (error) {
      console.error('[TIPOS MANTENIMIENTO] Error:', error);
      throw error;
    }
  }
};

// =================================================================================
// SERVICIOS DE ESTADOS DE ORDEN DE TRABAJO
// =================================================================================

export const estadosOrdenTrabajoServiceReal = {
  async getAll(params?: Record<string, any>): Promise<ApiResponse<EstadoOrdenTrabajo>> {
    try {
      console.log('[ESTADOS OT] Conectando al backend real...');
      const response = await apiClient.get('estados-orden-trabajo/', { params });
      console.log('[ESTADOS OT] Datos recibidos:', response.data);
      return response.data;
    } catch (error) {
      console.error('[ESTADOS OT] Error:', error);
      throw error;
    }
  }
};

// =================================================================================
// SERVICIOS DE USUARIOS
// =================================================================================

export const usuariosServiceReal = {
  async getAll(params?: Record<string, any>): Promise<ApiResponse<Usuario>> {
    try {
      console.log('[USUARIOS] Conectando al backend real...');
      const response = await apiClient.get('v2/usuarios/', { params });
      console.log('[USUARIOS] Datos recibidos:', response.data);
      return response.data;
    } catch (error) {
      console.error('[USUARIOS] Error:', error);
      throw error;
    }
  },

  async getById(id: number): Promise<Usuario> {
    try {
      const response = await apiClient.get(`v2/usuarios/${id}/`);
      return response.data;
    } catch (error) {
      console.error('[USUARIOS] Error:', error);
      throw error;
    }
  },

  async getTecnicos(): Promise<Usuario[]> {
    try {
      console.log('[USUARIOS] Obteniendo técnicos...');
      const response = await apiClient.get('v2/usuarios/tecnicos/');
      console.log('[USUARIOS] Técnicos recibidos:', response.data);
      return response.data;
    } catch (error) {
      console.error('[USUARIOS] Error obteniendo técnicos:', error);
      throw error;
    }
  }
};

// =================================================================================
// SERVICIOS DE ROLES
// =================================================================================

export const rolesServiceReal = {
  async getAll(params?: Record<string, any>): Promise<ApiResponse<Rol>> {
    try {
      console.log('[ROLES] Conectando al backend real...');
      const response = await apiClient.get('v2/roles/', { params });
      console.log('[ROLES] Datos recibidos:', response.data);
      return response.data;
    } catch (error) {
      console.error('[ROLES] Error:', error);
      throw error;
    }
  },

  async getById(id: number): Promise<Rol> {
    try {
      const response = await apiClient.get(`v2/roles/${id}/`);
      return response.data;
    } catch (error) {
      console.error('[ROLES] Error:', error);
      throw error;
    }
  }
};

// =================================================================================
// EXPORTAR TODOS LOS SERVICIOS
// =================================================================================

export default {
  equipos: equiposServiceReal,
  tiposEquipo: tiposEquipoServiceReal,
  estadosEquipo: estadosEquipoServiceReal,
  faenas: faenasServiceReal,
  ordenesTrabajo: ordenesTrabajoServiceReal,
  tiposMantenimientoOT: tiposMantenimientoOTServiceReal,
  estadosOrdenTrabajo: estadosOrdenTrabajoServiceReal,
  usuarios: usuariosServiceReal,
  roles: rolesServiceReal
};

