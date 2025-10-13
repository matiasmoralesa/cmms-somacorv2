import axios from 'axios';

// Se crea una instancia de Axios para centralizar la configuración de la API.
const apiClient = axios.create({
    baseURL: 'http://localhost:8000/api', // La URL base de tu backend de Django.
    timeout: 10000, // Timeout de 10 segundos
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
});

// Cache simple para evitar peticiones duplicadas
const requestCache = new Map();
const CACHE_DURATION = 30000; // 30 segundos

// Función para generar clave de caché
function getCacheKey(config: any): string {
    return `${config.method}_${config.url}_${JSON.stringify(config.params || {})}`;
}

// Interceptor para añadir el token de autenticación y caché
apiClient.interceptors.request.use(
    config => {
        const token = localStorage.getItem('authToken');
        if (token) {
            config.headers.Authorization = `Token ${token}`;
        }
        
        // Log de petición
        console.log(`🔵 [API] ${config.method?.toUpperCase()} ${config.url}`, {
            params: config.params,
            headers: config.headers,
            token: token ? 'Present' : 'None'
        });
        
        // Solo cachear peticiones GET
        if (config.method === 'get') {
            const cacheKey = getCacheKey(config);
            const cachedData = requestCache.get(cacheKey);
            
            if (cachedData && Date.now() - cachedData.timestamp < CACHE_DURATION) {
                console.log(`💾 [API] Using cached data for ${config.url}`);
                // Retornar datos cacheados
                return Promise.reject({
                    isCached: true,
                    data: cachedData.data
                });
            }
        }
        
        return config;
    }, 
    error => {
        console.error(`❌ [API] Request error:`, error);
        return Promise.reject(error);
    }
);

// Interceptor de respuesta para manejar caché y errores
apiClient.interceptors.response.use(
    response => {
        // Log de respuesta exitosa
        console.log(`✅ [API] ${response.config.method?.toUpperCase()} ${response.config.url} - Status: ${response.status}`, {
            data: response.data,
            size: JSON.stringify(response.data).length
        });
        
        // Guardar en caché las respuestas GET exitosas
        if (response.config.method === 'get') {
            const cacheKey = getCacheKey(response.config);
            requestCache.set(cacheKey, {
                data: response.data,
                timestamp: Date.now()
            });
            console.log(`💾 [API] Cached response for ${response.config.url}`);
        }
        
        return response;
    },
    error => {
        // Manejar datos cacheados
        if (error.isCached) {
            console.log(`💾 [API] Returning cached data for ${error.config?.url}`);
            return Promise.resolve({ data: error.data });
        }
        
        // Log de error
        console.error(`❌ [API] ${error.config?.method?.toUpperCase()} ${error.config?.url} - Error:`, {
            status: error.response?.status,
            statusText: error.response?.statusText,
            data: error.response?.data,
            message: error.message
        });
        
        // Manejar errores de timeout
        if (error.code === 'ECONNABORTED') {
            console.error('⏰ [API] Request timeout:', error.config.url);
            return Promise.reject({
                ...error,
                message: 'La petición tardó demasiado tiempo. Por favor, intenta nuevamente.'
            });
        }
        
        // Manejar errores de conexión
        if (!error.response) {
            console.error('🌐 [API] Network error:', error.message);
            return Promise.reject({
                ...error,
                message: 'Error de conexión. Verifica tu conexión a internet.'
            });
        }
        
        return Promise.reject(error);
    }
);

// Función para limpiar caché
export const clearCache = () => {
    requestCache.clear();
};

// Función para obtener estadísticas del caché
export const getCacheStats = () => {
    return {
        size: requestCache.size,
        entries: Array.from(requestCache.keys())
    };
};

export default apiClient;