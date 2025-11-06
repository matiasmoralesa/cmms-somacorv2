/**
 * Servicio para gestionar tipos de equipo
 */

import apiClient from '@/api/apiClient';

export interface TipoEquipo {
  id?: number;
  nombre: string;
  descripcion?: string;
  categoria: string;
  activo: boolean;
}

class TiposEquipoService {
  private baseUrl = '/v2/tipos-equipo';

  async getAll(params?: any): Promise<{results: TipoEquipo[], count: number}> {
    const response = await apiClient.get(this.baseUrl, { params });
    return response.data;
  }

  async getById(id: number): Promise<TipoEquipo> {
    const response = await apiClient.get(`${this.baseUrl}/${id}/`);
    return response.data;
  }

  async create(data: Omit<TipoEquipo, 'id'>): Promise<TipoEquipo> {
    const response = await apiClient.post(this.baseUrl, data);
    return response.data;
  }

  async update(id: number, data: Partial<TipoEquipo>): Promise<TipoEquipo> {
    const response = await apiClient.put(`${this.baseUrl}/${id}/`, data);
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}/`);
  }
}

export const tiposEquipoService = new TiposEquipoService();

