// src/hooks/useOptimizedApi.ts
// Hook optimizado para llamadas API con caché y debouncing

import { useState, useEffect, useCallback, useRef } from 'react';

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiry: number;
}

class ApiCache {
  private cache = new Map<string, CacheEntry<any>>();
  private readonly DEFAULT_EXPIRY = 5 * 60 * 1000; // 5 minutos

  set<T>(key: string, data: T, expiry?: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      expiry: expiry || this.DEFAULT_EXPIRY
    });
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    const now = Date.now();
    if (now - entry.timestamp > entry.expiry) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  clear(): void {
    this.cache.clear();
  }

  delete(key: string): void {
    this.cache.delete(key);
  }
}

const apiCache = new ApiCache();

interface UseOptimizedApiOptions {
  cacheKey?: string;
  cacheExpiry?: number;
  debounceMs?: number;
  enabled?: boolean;
}

export function useOptimizedApi<T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = [],
  options: UseOptimizedApiOptions = {}
) {
  const {
    cacheKey,
    cacheExpiry,
    debounceMs = 300,
    enabled = true
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const fetchData = useCallback(async () => {
    if (!enabled) return;

    // Verificar caché si existe cacheKey
    if (cacheKey) {
      const cachedData = apiCache.get<T>(cacheKey);
      if (cachedData) {
        setData(cachedData);
        setLoading(false);
        setError(null);
        return;
      }
    }

    // Cancelar request anterior si existe
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Crear nuevo AbortController
    abortControllerRef.current = new AbortController();

    setLoading(true);
    setError(null);

    try {
      const result = await apiCall();
      
      // Verificar si el request no fue cancelado
      if (!abortControllerRef.current?.signal.aborted) {
        setData(result);
        
        // Guardar en caché si existe cacheKey
        if (cacheKey) {
          apiCache.set(cacheKey, result, cacheExpiry);
        }
      }
    } catch (err: any) {
      if (!abortControllerRef.current?.signal.aborted) {
        setError(err.message || 'Error al cargar datos');
        console.error('Error en useOptimizedApi:', err);
      }
    } finally {
      if (!abortControllerRef.current?.signal.aborted) {
        setLoading(false);
      }
    }
  }, [apiCall, enabled, cacheKey, cacheExpiry]);

  const debouncedFetchData = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      fetchData();
    }, debounceMs);
  }, [fetchData, debounceMs]);

  useEffect(() => {
    debouncedFetchData();

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, dependencies);

  const refetch = useCallback(() => {
    if (cacheKey) {
      apiCache.delete(cacheKey);
    }
    fetchData();
  }, [fetchData, cacheKey]);

  const clearCache = useCallback(() => {
    if (cacheKey) {
      apiCache.delete(cacheKey);
    }
  }, [cacheKey]);

  return {
    data,
    loading,
    error,
    refetch,
    clearCache
  };
}

// Hook para invalidar caché relacionado
export function useInvalidateCache() {
  return useCallback((pattern?: string) => {
    if (pattern) {
      // Implementar invalidación por patrón si es necesario
      apiCache.clear();
    } else {
      apiCache.clear();
    }
  }, []);
}

export default useOptimizedApi;

