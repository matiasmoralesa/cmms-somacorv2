// src/hooks/index.ts
// Hooks personalizados para gestión de estado y llamadas API

import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  equiposService,
  tiposEquipoService,
  estadosEquipoService,
  faenasService,
  planesMantenimientoService,
  ordenesTrabajoService,
  checklistService,
  dashboardService,
  tareasEstandarService,
  userService
} from '../services/apiService';
import type {
  Equipo,
  TipoEquipo,
  EstadoEquipo,
  Faena,
  PlanMantenimiento,
  OrdenTrabajo,
  ChecklistTemplate,
  ChecklistInstance,
  DashboardStats,
  TareaEstandar,
  User,
  ApiResponse
} from '../types';

// Hook genérico para operaciones CRUD
export function useApiData<T>(
  service: any,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await service.getAll();
      setData(response.results || response);
    } catch (err: any) {
      setError(err.message || 'Error al cargar los datos');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const create = useCallback(async (item: Partial<T>) => {
    try {
      const newItem = await service.create(item);
      setData(prev => [...prev, newItem]);
      return newItem;
    } catch (err: any) {
      setError(err.message || 'Error al crear el elemento');
      throw err;
    }
  }, [service]);

  const update = useCallback(async (id: number, item: Partial<T>) => {
    try {
      const updatedItem = await service.update(id, item);
      setData(prev => prev.map(i => (i as any).id === id ? updatedItem : i));
      return updatedItem;
    } catch (err: any) {
      setError(err.message || 'Error al actualizar el elemento');
      throw err;
    }
  }, [service]);

  const remove = useCallback(async (id: number) => {
    try {
      await service.delete(id);
      setData(prev => prev.filter(i => (i as any).id !== id));
    } catch (err: any) {
      setError(err.message || 'Error al eliminar el elemento');
      throw err;
    }
  }, [service]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
    create,
    update,
    remove
  };
}

// Hooks específicos para cada módulo
export function useEquipos() {
  return useApiData<Equipo>(equiposService);
}

export function useTiposEquipo() {
  return useApiData<TipoEquipo>(tiposEquipoService);
}

export function useEstadosEquipo() {
  return useApiData<EstadoEquipo>(estadosEquipoService);
}

export function useFaenas() {
  return useApiData<Faena>(faenasService);
}

export function usePlanesMantenimiento() {
  return useApiData<PlanMantenimiento>(planesMantenimientoService);
}

export function useOrdenesTrabajoData() {
  return useApiData<OrdenTrabajo>(ordenesTrabajoService);
}

export function useTareasEstandar() {
  return useApiData<TareaEstandar>(tareasEstandarService);
}

export function useUsuarios() {
  return useApiData<User>(userService);
}

// Hook para dashboard
export function useDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardService.getStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Error al cargar estadísticas');
      console.error('Error fetching dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return { stats, loading, error, refetch: fetchStats };
}

// Hook para checklist templates por equipo
export function useChecklistTemplates(equipoId?: number) {
  const [templates, setTemplates] = useState<ChecklistTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTemplates = useCallback(async () => {
    if (!equipoId) {
      setTemplates([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await checklistService.getTemplatesPorEquipo(equipoId);
      setTemplates(data);
    } catch (err: any) {
      setError(err.message || 'Error al cargar plantillas de checklist');
      console.error('Error fetching checklist templates:', err);
    } finally {
      setLoading(false);
    }
  }, [equipoId]);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  return { templates, loading, error, refetch: fetchTemplates };
}

// Hook para historial de checklist
export function useChecklistHistorial(equipoId?: number, fechaInicio?: string, fechaFin?: string) {
  const [historial, setHistorial] = useState<ChecklistInstance[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHistorial = useCallback(async () => {
    if (!equipoId) {
      setHistorial([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await checklistService.getHistorialEquipo(equipoId, fechaInicio, fechaFin);
      setHistorial(data);
    } catch (err: any) {
      setError(err.message || 'Error al cargar historial de checklist');
      console.error('Error fetching checklist history:', err);
    } finally {
      setLoading(false);
    }
  }, [equipoId, fechaInicio, fechaFin]);

  useEffect(() => {
    fetchHistorial();
  }, [fetchHistorial]);

  return { historial, loading, error, refetch: fetchHistorial };
}

// Hook para órdenes de trabajo con filtros
export function useOrdenesTrabajoFiltradas(filtros?: {
  estado?: number;
  equipo?: number;
  fechaInicio?: string;
  fechaFin?: string;
}) {
  const [ordenes, setOrdenes] = useState<OrdenTrabajo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOrdenes = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await ordenesTrabajoService.getAll(filtros);
      setOrdenes(Array.isArray(response) ? response : response.results || []);
    } catch (err: any) {
      setError(err.message || 'Error al cargar órdenes de trabajo');
      console.error('Error fetching work orders:', err);
    } finally {
      setLoading(false);
    }
  }, [filtros]);

  useEffect(() => {
    fetchOrdenes();
  }, [fetchOrdenes]);

  return { ordenes, loading, error, refetch: fetchOrdenes };
}

// Hook para equipos críticos
export function useEquiposCriticos() {
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEquiposCriticos = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await equiposService.getEquiposCriticos();
      setEquipos(data);
    } catch (err: any) {
      setError(err.message || 'Error al cargar equipos críticos');
      console.error('Error fetching critical equipment:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEquiposCriticos();
  }, [fetchEquiposCriticos]);

  return { equipos, loading, error, refetch: fetchEquiposCriticos };
}

// Hook para gestión de formularios
export function useForm<T>(initialValues: T) {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});

  const setValue = useCallback((name: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
    // Limpiar error cuando el usuario empieza a escribir
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  }, [errors]);

  const setError = useCallback((name: keyof T, error: string) => {
    setErrors(prev => ({ ...prev, [name]: error }));
  }, []);

  const setTouchedField = useCallback((name: keyof T) => {
    setTouched(prev => ({ ...prev, [name]: true }));
  }, []);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  const isValid = useMemo(() => {
    return Object.keys(errors).length === 0;
  }, [errors]);

  return {
    values,
    errors,
    touched,
    setValue,
    setError,
    setTouched: setTouchedField,
    reset,
    isValid
  };
}

// Hook para paginación
export function usePagination<T>(data: T[], itemsPerPage: number = 10) {
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(data.length / itemsPerPage);
  
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return data.slice(startIndex, startIndex + itemsPerPage);
  }, [data, currentPage, itemsPerPage]);

  const goToPage = useCallback((page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  }, [totalPages]);

  const nextPage = useCallback(() => {
    goToPage(currentPage + 1);
  }, [currentPage, goToPage]);

  const prevPage = useCallback(() => {
    goToPage(currentPage - 1);
  }, [currentPage, goToPage]);

  return {
    currentPage,
    totalPages,
    paginatedData,
    goToPage,
    nextPage,
    prevPage,
    hasNext: currentPage < totalPages,
    hasPrev: currentPage > 1
  };
}

