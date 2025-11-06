// src/utils/auth.ts

export interface UserInfo {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
}

export interface RoleInfo {
  id: number | null;
  nombre: string;
  departamento: string;
}

export interface AuthData {
  token: string;
  user: UserInfo;
  rol: RoleInfo;
}

// Verificar si el usuario está autenticado
export const isAuthenticated = (): boolean => {
  const token = localStorage.getItem('authToken');
  return !!token;
};

// Obtener el token de autenticación
export const getAuthToken = (): string | null => {
  return localStorage.getItem('authToken');
};

// Obtener información del usuario
export const getUserInfo = (): UserInfo | null => {
  const userInfo = localStorage.getItem('userInfo');
  return userInfo ? JSON.parse(userInfo) : null;
};

// Obtener información del rol
export const getUserRole = (): RoleInfo | null => {
  const roleInfo = localStorage.getItem('userRole');
  return roleInfo ? JSON.parse(roleInfo) : null;
};

// Verificar si el usuario tiene un rol específico
export const hasRole = (roleName: string): boolean => {
  const role = getUserRole();
  return role?.nombre === roleName;
};

export const isAdmin = (): boolean => {
  return hasRole("Administrador");
};

// Verificar si el usuario es Supervisor
export const isSupervisor = (): boolean => {
  return hasRole("Supervisor");
};

// Verificar si el usuario es Operador
export const isOperador = (): boolean => {
  return hasRole('Operador');
};

// Verificar si el usuario es Admin o Supervisor
export const isAdminOrSupervisor = (): boolean => {
  return isAdmin() || isSupervisor();
};

// Cerrar sesión
export const logout = (): void => {
  localStorage.removeItem('authToken');
  localStorage.removeItem('userInfo');
  localStorage.removeItem('userRole');
  // Redireccionar al login
  window.location.href = '/login';
};

// Obtener headers de autenticación para las peticiones API
export const getAuthHeaders = (): Record<string, string> => {
  const token = getAuthToken();
  return token ? {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  } : {
    'Content-Type': 'application/json'
  };
};

// Verificar permisos para acceder a una ruta específica
export const canAccessRoute = (routePath: string): boolean => {
  const role = getUserRole();
  if (!role) {
    return false;
  }

  // El administrador tiene acceso completo a todo el sistema
  if (role.nombre === 'Administrador' || role.nombre === 'Admin') {
    return true;
  }

  // Definir qué rutas puede acceder cada rol (excluyendo administrador que ya tiene acceso total)
  const routePermissions: Record<string, string[]> = {
    '/dashboard': ['Supervisor'],
    '/estado-maquina': ['Supervisor', 'Operador', 'Técnico'],
    '/checklist': ['Supervisor', 'Operador', 'Técnico'],
    '/ordenes-trabajo': ['Supervisor', 'Operador', 'Técnico'],
    '/calendario': ['Supervisor', 'Operador', 'Técnico'],
    '/mantenimiento-planificado': ['Supervisor'],
    '/mantenimiento-no-planificado': ['Supervisor', 'Operador', 'Técnico'],
    '/control/ordenes-trabajo': ['Supervisor', 'Operador', 'Técnico'],
    '/control/checklist-diario': ['Supervisor', 'Operador', 'Técnico'],
    '/control/crear-mantenimiento': ['Supervisor'],
    '/control/reportar-falla': ['Supervisor', 'Operador', 'Técnico'],
    '/control/calendario': ['Supervisor', 'Operador', 'Técnico'],
    '/administracion': ['Supervisor'],
    '/administracion/perfiles': ['Supervisor'],
    '/administracion/equipos-moviles': ['Supervisor'],
    '/administracion/programas-mantenimiento': ['Supervisor']
  };

  const allowedRoles = routePermissions[routePath];
  return allowedRoles ? allowedRoles.includes(role.nombre) : false;
};

// Obtener la ruta de redirección por defecto según el rol
export const getDefaultRoute = (): string => {
  const role = getUserRole();
  if (!role) {
    return '/login';
  }

  switch (role.nombre) {
    case 'Admin':
    case 'Administrador':
    case 'Supervisor':
      return '/dashboard'; // Administradores y Supervisores van al Dashboard
    case 'Operador':
    case 'Técnico':
      return '/estado-maquina'; // Operadores y Técnicos van al Estado de la Máquina
    default:
      return '/estado-maquina'; // Por defecto, ir al Estado de la Máquina
  }
};

