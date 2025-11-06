/**
 * Servicio para gestionar técnicos
 */

import apiClient from '@/api/apiClient';

export interface Tecnico {
  id?: number;
  usuario: number;
  especialidad: number;
  disponibilidad: 'disponible' | 'ocupado' | 'no_disponible';
  telefono?: string;
  email?: string;
  cargo?: string;
}

class TecnicosService {
  private baseUrl = '/v2/tecnicos';

  async getAll(params?: any): Promise<{results: Tecnico[], count: number}> {
    const response = await apiClient.get(this.baseUrl, { params });
    return response.data;
  }

  async getById(id: number): Promise<Tecnico> {
    const response = await apiClient.get(`${this.baseUrl}/${id}/`);
    return response.data;
  }

  async create(data: Omit<Tecnico, 'id'>): Promise<Tecnico> {
    const response = await apiClient.post(this.baseUrl, data);
    return response.data;
  }

  async update(id: number, data: Partial<Tecnico>): Promise<Tecnico> {
    const response = await apiClient.put(`${this.baseUrl}/${id}/`, data);
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}/`);
  }

  async updateDisponibilidad(id: number, disponibilidad: string): Promise<Tecnico> {
    const response = await apiClient.patch(`${this.baseUrl}/${id}/`, { disponibilidad });
    return response.data;
  }

  async getDisponibles(): Promise<Tecnico[]> {
    const response = await apiClient.get(`${this.baseUrl}/?disponibilidad=disponible`);
    return response.data.results;
  }
}

export const tecnicosService = new TecnicosService();

