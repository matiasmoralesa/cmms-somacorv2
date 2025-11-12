/**
 * Servicio para gestionar inventario
 */

import apiClient from '@/api/apiClient';

export interface ItemInventario {
  id?: number;
  codigo: string;
  nombre: string;
  categoria: string;
  stock_actual: number;
  stock_minimo: number;
  unidad: string;
  ubicacion: string;
  proveedor?: string;
  precio_unitario?: number;
  estado: 'disponible' | 'bajo_stock' | 'agotado';
}

export interface MovimientoInventario {
  id?: number;
  item: number;
  tipo: 'entrada' | 'salida';
  cantidad: number;
  motivo: string;
  fecha: string;
  usuario: string;
}

class InventarioService {
  private baseUrl = '/v2/inventario/';

  async getAll(params?: any): Promise<{results: ItemInventario[], count: number}> {
    const response = await apiClient.get(this.baseUrl, { params });
    return response.data;
  }

  async getById(id: number): Promise<ItemInventario> {
    const response = await apiClient.get(`${this.baseUrl}/${id}/`);
    return response.data;
  }

  async create(data: Omit<ItemInventario, 'id'>): Promise<ItemInventario> {
    const response = await apiClient.post(this.baseUrl.replace(/\/$/, ''), data);
    return response.data;
  }

  async update(id: number, data: Partial<ItemInventario>): Promise<ItemInventario> {
    const response = await apiClient.put(`${this.baseUrl}/${id}/`, data);
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}/`);
  }

  async registrarMovimiento(data: Omit<MovimientoInventario, 'id'>): Promise<MovimientoInventario> {
    const response = await apiClient.post(`${this.baseUrl}/movimientos/`, data);
    return response.data;
  }

  async getMovimientos(itemId?: number): Promise<MovimientoInventario[]> {
    const params = itemId ? { item: itemId } : {};
    const response = await apiClient.get(`${this.baseUrl}/movimientos/`, { params });
    return response.data;
  }
}

export const inventarioService = new InventarioService();

