/**
 * Servicio para gestionar planes de mantenimiento
 */

import apiClient from '@/api/apiClient';

export interface PlanMantenimiento {
  id?: number;
  nombre: string;
  equipo: number;
  frecuencia: string;
  descripcion: string;
  duracion_estimada: string;
  activo: boolean;
  proxima_ejecucion?: string;
  ultima_ejecucion?: string;
}

export interface PlanMantenimientoResponse {
  results: PlanMantenimiento[];
  count: number;
  next: string | null;
  previous: string | null;
}

class PlanesMantenimientoService {
  private baseUrl = '/v2/planes-mantenimiento';

  /**
   * Obtener todos los planes de mantenimiento
   */
  async getAll(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    activo?: boolean;
  }): Promise<PlanMantenimientoResponse> {
    try {
      const response = await apiClient.get(this.baseUrl, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching planes de mantenimiento:', error);
      throw error;
    }
  }

  /**
   * Obtener un plan de mantenimiento por ID
   */
  async getById(id: number): Promise<PlanMantenimiento> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching plan de mantenimiento ${id}:`, error);
      throw error;
    }
  }

  /**
   * Crear un nuevo plan de mantenimiento
   */
  async create(data: Omit<PlanMantenimiento, 'id'>): Promise<PlanMantenimiento> {
    try {
      const response = await apiClient.post(this.baseUrl, data);
      return response.data;
    } catch (error) {
      console.error('Error creating plan de mantenimiento:', error);
      throw error;
    }
  }

  /**
   * Actualizar un plan de mantenimiento
   */
  async update(id: number, data: Partial<PlanMantenimiento>): Promise<PlanMantenimiento> {
    try {
      const response = await apiClient.put(`${this.baseUrl}/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error(`Error updating plan de mantenimiento ${id}:`, error);
      throw error;
    }
  }

  /**
   * Eliminar un plan de mantenimiento
   */
  async delete(id: number): Promise<void> {
    try {
      await apiClient.delete(`${this.baseUrl}/${id}/`);
    } catch (error) {
      console.error(`Error deleting plan de mantenimiento ${id}:`, error);
      throw error;
    }
  }

  /**
   * Toggle estado activo/inactivo de un plan
   */
  async toggleActivo(id: number, activo: boolean): Promise<PlanMantenimiento> {
    try {
      const response = await apiClient.patch(`${this.baseUrl}/${id}/`, { activo });
      return response.data;
    } catch (error) {
      console.error(`Error toggling plan de mantenimiento ${id}:`, error);
      throw error;
    }
  }

  /**
   * Obtener estadísticas de planes de mantenimiento
   */
  async getStats(): Promise<{
    total: number;
    activos: number;
    inactivos: number;
    proximos: number;
    vencidos: number;
  }> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/stats/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching planes de mantenimiento stats:', error);
      throw error;
    }
  }
}

export const planesMantenimientoService = new PlanesMantenimientoService();

