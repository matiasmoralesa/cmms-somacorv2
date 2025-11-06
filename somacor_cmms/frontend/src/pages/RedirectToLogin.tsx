import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const RedirectToLogin: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Limpiar todo el almacenamiento
    localStorage.clear();
    sessionStorage.clear();
    
    // Redireccionar al login después de un breve delay
    const timer = setTimeout(() => {
      navigate('/login', { replace: true });
    }, 1000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-700 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-md p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold text-gray-800 mb-2">Preparando el sistema...</h2>
        <p className="text-gray-600">Redirigiendo al login</p>
      </div>
    </div>
  );
};

export default RedirectToLogin;