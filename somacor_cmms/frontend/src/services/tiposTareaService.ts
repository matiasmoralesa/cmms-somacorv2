/**
 * Servicio para gestionar tipos de tarea
 */

import apiClient from '@/api/apiClient';

export interface TipoTarea {
  id?: number;
  nombre: string;
  descripcion?: string;
  duracion_estimada: string;
  categoria: string;
  activo: boolean;
}

class TiposTareaService {
  private baseUrl = '/v2/tipos-tarea';

  async getAll(params?: any): Promise<{results: TipoTarea[], count: number}> {
    const response = await apiClient.get(this.baseUrl, { params });
    return response.data;
  }

  async getById(id: number): Promise<TipoTarea> {
    const response = await apiClient.get(`${this.baseUrl}/${id}/`);
    return response.data;
  }

  async create(data: Omit<TipoTarea, 'id'>): Promise<TipoTarea> {
    const response = await apiClient.post(this.baseUrl, data);
    return response.data;
  }

  async update(id: number, data: Partial<TipoTarea>): Promise<TipoTarea> {
    const response = await apiClient.put(`${this.baseUrl}/${id}/`, data);
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}/`);
  }
}

export const tiposTareaService = new TiposTareaService();

