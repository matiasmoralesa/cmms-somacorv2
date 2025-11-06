import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { isAuthenticated, canAccessRoute } from '../utils/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRoles }) => {
  const location = useLocation();

  // Verificar si el usuario está autenticado
  if (!isAuthenticated()) {
    // Redireccionar al login, guardando la ruta actual para redireccionar después del login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Verificar si el usuario tiene permisos para acceder a esta ruta
  if (!canAccessRoute(location.pathname)) {
    // Redireccionar a una página de acceso denegado o a la ruta por defecto
    return <Navigate to="/acceso-denegado" replace />;
  }

  // Si está autenticado y tiene permisos, mostrar el contenido
  return <>{children}</>;
};

export default ProtectedRoute;

