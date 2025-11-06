/**
 * Servicio para gestionar perfiles de usuario
 */

import apiClient from '@/api/apiClient';

export interface Perfil {
  id?: number;
  usuario: number;
  rol: number;
  especialidad?: number;
  telefono?: string;
  cargo?: string;
  activo: boolean;
}

export interface Rol {
  id?: number;
  nombre: string;
  descripcion?: string;
  permisos: string[];
}

class PerfilesService {
  private baseUrl = '/v2/perfiles';

  async getAll(params?: any): Promise<{results: Perfil[], count: number}> {
    const response = await apiClient.get(this.baseUrl, { params });
    return response.data;
  }

  async getById(id: number): Promise<Perfil> {
    const response = await apiClient.get(`${this.baseUrl}/${id}/`);
    return response.data;
  }

  async create(data: Omit<Perfil, 'id'>): Promise<Perfil> {
    const response = await apiClient.post(this.baseUrl, data);
    return response.data;
  }

  async update(id: number, data: Partial<Perfil>): Promise<Perfil> {
    const response = await apiClient.put(`${this.baseUrl}/${id}/`, data);
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}/`);
  }

  // Roles
  async getRoles(): Promise<Rol[]> {
    const response = await apiClient.get(`${this.baseUrl}/roles/`);
    return response.data;
  }
}

export const perfilesService = new PerfilesService();

