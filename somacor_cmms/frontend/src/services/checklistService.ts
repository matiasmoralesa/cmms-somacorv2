/**
 * Servicio para gestionar checklist
 */

import apiClient from '@/api/apiClient';

export interface ChecklistCategory {
  id?: number;
  nombre: string;
  descripcion?: string;
  orden: number;
}

export interface ChecklistItem {
  id?: number;
  categoria: number;
  nombre: string;
  descripcion?: string;
  tipo: 'verificacion' | 'medicion' | 'observacion';
  orden: number;
  activo: boolean;
}

export interface ChecklistInstance {
  id?: number;
  checklist: number;
  equipo: number;
  fecha: string;
  tecnico: number;
  completado: boolean;
  observaciones?: string;
  imagenes?: string[];
}

export interface ChecklistAnswer {
  id?: number;
  instancia: number;
  item: number;
  respuesta: string;
  valor?: string;
  unidad?: string;
  imagen?: string;
}

class ChecklistService {
  private baseUrl = '/v2/checklist';

  // Categorías
  async getCategories(): Promise<ChecklistCategory[]> {
    const response = await apiClient.get(`${this.baseUrl}/categorias/`);
    return response.data;
  }

  async createCategory(data: Omit<ChecklistCategory, 'id'>): Promise<ChecklistCategory> {
    const response = await apiClient.post(`${this.baseUrl}/categorias/`, data);
    return response.data;
  }

  // Items
  async getItems(categoriaId?: number): Promise<ChecklistItem[]> {
    const params = categoriaId ? { categoria: categoriaId } : {};
    const response = await apiClient.get(`${this.baseUrl}/items/`, { params });
    return response.data;
  }

  async createItem(data: Omit<ChecklistItem, 'id'>): Promise<ChecklistItem> {
    const response = await apiClient.post(`${this.baseUrl}/items/`, data);
    return response.data;
  }

  // Instancias
  async getInstances(params?: any): Promise<{results: ChecklistInstance[], count: number}> {
    const response = await apiClient.get(`${this.baseUrl}/instancias/`, { params });
    return response.data;
  }

  async createInstance(data: Omit<ChecklistInstance, 'id'>): Promise<ChecklistInstance> {
    const response = await apiClient.post(`${this.baseUrl}/instancias/`, data);
    return response.data;
  }

  async completeInstance(id: number, data: Partial<ChecklistInstance>): Promise<ChecklistInstance> {
    const response = await apiClient.patch(`${this.baseUrl}/instancias/${id}/`, data);
    return response.data;
  }

  // Respuestas
  async getAnswers(instanciaId: number): Promise<ChecklistAnswer[]> {
    const response = await apiClient.get(`${this.baseUrl}/respuestas/?instancia=${instanciaId}`);
    return response.data;
  }

  async saveAnswer(data: Omit<ChecklistAnswer, 'id'>): Promise<ChecklistAnswer> {
    const response = await apiClient.post(`${this.baseUrl}/respuestas/`, data);
    return response.data;
  }
}

export const checklistService = new ChecklistService();

