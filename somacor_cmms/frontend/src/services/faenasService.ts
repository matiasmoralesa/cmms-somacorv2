/**
 * Servicio para gestionar faenas
 */

import apiClient from '@/api/apiClient';

export interface Faena {
  id?: number;
  nombre: string;
  ubicacion: string;
  descripcion?: string;
  activa: boolean;
}

class FaenasService {
  private baseUrl = '/v2/faenas';

  async getAll(params?: any): Promise<{results: Faena[], count: number}> {
    const response = await apiClient.get(this.baseUrl, { params });
    return response.data;
  }

  async getById(id: number): Promise<Faena> {
    const response = await apiClient.get(`${this.baseUrl}/${id}/`);
    return response.data;
  }

  async create(data: Omit<Faena, 'id'>): Promise<Faena> {
    const response = await apiClient.post(this.baseUrl, data);
    return response.data;
  }

  async update(id: number, data: Partial<Faena>): Promise<Faena> {
    const response = await apiClient.put(`${this.baseUrl}/${id}/`, data);
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}/`);
  }
}

export const faenasService = new FaenasService();

