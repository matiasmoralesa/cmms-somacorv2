import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, User, Lock, AlertCircle } from 'lucide-react';
import apiClient from '@/api/apiClient';

const LoginView: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Limpiar error cuando el usuario empiece a escribir
    if (error) setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      console.log('🔵 [LOGIN] Intentando login con usuario:', formData.username);
      
      const response = await apiClient.post('/login/', {
        username: formData.username,
        password: formData.password
      });

      console.log('✅ [LOGIN] Login exitoso:', response.data);

      const data = response.data;

      // Guardar información de autenticación en localStorage
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('userInfo', JSON.stringify(data.user));
      localStorage.setItem('userRole', JSON.stringify(data.rol));

      // Redireccionar según el rol del usuario
      const rolNombre = data.rol?.nombre || 'default';
      console.log('🔵 [LOGIN] Rol del usuario:', rolNombre);
      
      switch (rolNombre) {
        case 'Admin':
        case 'Administrador':
        case 'Supervisor':
          navigate('/dashboard');
          break;
        case 'Operador':
          navigate('/estado-maquina');
          break;
        case 'Técnico':
          navigate('/estado-maquina');
          break;
        default:
          navigate('/dashboard');
      }
    } catch (error: any) {
      console.error('❌ [LOGIN] Error de login:', error);
      
      if (error.response) {
        // El servidor respondió con un código de error
        const errorMessage = error.response.data?.detail || 
                           error.response.data?.message || 
                           error.response.data?.error ||
                           'Error en las credenciales';
        setError(errorMessage);
        console.error('❌ [LOGIN] Error del servidor:', error.response.status, errorMessage);
      } else if (error.request) {
        // La petición se hizo pero no hubo respuesta
        setError('Error de conexión. Verifica que el servidor esté corriendo.');
        console.error('❌ [LOGIN] Sin respuesta del servidor');
      } else {
        // Algo pasó al configurar la petición
        setError('Error de conexión. Por favor, intente nuevamente.');
        console.error('❌ [LOGIN] Error:', error.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-md p-8">
        {/* Logo y título */}
        <div className="text-center mb-8">
          <div className="bg-blue-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl font-bold">S</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Somacor CMMS</h1>
          <p className="text-gray-600">Sistema de Gestión de Mantenimiento</p>
        </div>

        {/* Formulario de login */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Campo de usuario */}
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Usuario
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Ingrese su usuario"
                required
              />
            </div>
          </div>

          {/* Campo de contraseña */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Contraseña
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="block w-full pl-10 pr-10 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Ingrese su contraseña"
                required
              />
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                <button
                  type="button"
                  className="text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Mensaje de error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3 flex items-center">
              <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
              <span className="text-sm text-red-600">{error}</span>
            </div>
          )}

          {/* Botón de login */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Iniciando sesión...
              </div>
            ) : (
              'Iniciar Sesión'
            )}
          </button>
        </form>

        {/* Credenciales de prueba */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <h3 className="text-sm font-medium text-blue-800 mb-2">Credenciales de Prueba:</h3>
          <div className="text-xs text-blue-700 space-y-1">
            <p><strong>Usuario:</strong> admin</p>
            <p><strong>Contraseña:</strong> admin123</p>
          </div>
          <button
            type="button"
            onClick={() => {
              setFormData({ username: 'admin', password: 'admin123' });
            }}
            className="mt-2 text-xs text-blue-600 hover:text-blue-800 underline"
          >
            Usar credenciales de prueba
          </button>
        </div>

        {/* Información adicional */}
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            ¿Problemas para acceder? Contacte al administrador del sistema.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginView;

