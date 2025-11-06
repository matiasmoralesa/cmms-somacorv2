import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, ArrowLeft, Home } from 'lucide-react';
import { getDefaultRoute, getUserRole } from '../utils/auth';

const AccesoDenegadoView: React.FC = () => {
  const navigate = useNavigate();
  const userRole = getUserRole();

  const handleGoBack = () => {
    navigate(-1);
  };

  const handleGoHome = () => {
    const defaultRoute = getDefaultRoute();
    navigate(defaultRoute);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-8 text-center">
        {/* Icono de acceso denegado */}
        <div className="bg-red-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
          <Shield className="h-10 w-10 text-red-600" />
        </div>

        {/* Título y mensaje */}
        <h1 className="text-2xl font-bold text-gray-800 mb-4">
          Acceso Denegado
        </h1>
        <p className="text-gray-600 mb-2">
          No tienes permisos para acceder a esta página.
        </p>
        <p className="text-sm text-gray-500 mb-8">
          Tu rol actual: <span className="font-medium">{userRole?.nombre || 'Sin rol asignado'}</span>
        </p>

        {/* Botones de acción */}
        <div className="space-y-3">
          <button
            onClick={handleGoHome}
            className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <Home className="h-4 w-4 mr-2" />
            Ir al Inicio
          </button>
          
          <button
            onClick={handleGoBack}
            className="w-full flex items-center justify-center px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver Atrás
          </button>
        </div>

        {/* Información adicional */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            Si crees que esto es un error, contacta al administrador del sistema.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AccesoDenegadoView;

