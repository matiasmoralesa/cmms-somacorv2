// src/context/AuthContext.tsx
// MODIFICADO: Se ha añadido un objeto 'mockUser' (usuario simulado) para que la
// aplicación funcione sin un inicio de sesión real. Este usuario se usa como
// estado inicial, permitiendo que la interfaz de usuario muestre información
// coherente y evitando errores por datos de usuario nulos.

import React, { createContext, useState, useEffect, ReactNode, useContext } from 'react';
import apiClient from '../api/apiClient';

// Definición de la interfaz para el objeto de usuario.
interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    usuarios: { // Perfil de usuario extendido
        idrol: number;
        nombrerol: string;
        idespecialidad: number | null;
        telefono: string | null;
        cargo: string | null;
    };
}

// Definición de la interfaz para el contexto de autenticación.
interface AuthContextType {
    user: User | null;
    token: string | null;
    isLoading: boolean;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Objeto de usuario simulado para desarrollo sin autenticación.
const mockUser: User = {
    id: 0,
    username: 'Usuario Local',
    email: 'local@user.com',
    first_name: 'Usuario',
    last_name: 'Local',
    usuarios: {
        idrol: 1, // Se asume que el rol 1 es 'Administrador' o un rol con acceso total.
        nombrerol: 'Administrador',
        idespecialidad: null,
        telefono: null,
        cargo: 'Developer'
    }
};

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    // El estado del usuario se inicializa con el usuario simulado.
    const [user, setUser] = useState<User | null>(mockUser);
    const [token, setToken] = useState<string | null>(localStorage.getItem('authToken'));
    // isLoading se establece en 'false' para evitar la pantalla de carga.
    const [isLoading, setIsLoading] = useState(false);

    // useEffect se mantiene para manejar la restauración de una sesión real si existiera.
    useEffect(() => {
        const storedToken = localStorage.getItem('authToken');
        const storedUser = localStorage.getItem('user');

        if (storedToken && storedUser) {
            try {
                // Si hay un usuario real en localStorage, se usa.
                const parsedUser: User = JSON.parse(storedUser);
                setUser(parsedUser);
                setToken(storedToken);
                apiClient.defaults.headers.common['Authorization'] = `Token ${storedToken}`;
            } catch (error) {
                // Si falla la carga, se usan los valores por defecto (mockUser).
                setUser(mockUser);
                setToken(null);
            }
        }
        setIsLoading(false);
    }, []);

    // La función de login sigue funcionando para permitir iniciar sesión si se desea.
    const login = async (username: string, password: string) => {
        const response = await apiClient.post<{ token: string; user: User }>('/login/', { username, password });
        const { token: newToken, user: newUser } = response.data;
        localStorage.setItem('authToken', newToken);
        localStorage.setItem('user', JSON.stringify(newUser));
        setToken(newToken);
        setUser(newUser);
        apiClient.defaults.headers.common['Authorization'] = `Token ${newToken}`;
    };

    // Al cerrar sesión, se vuelve al usuario simulado.
    const logout = () => {
        apiClient.post('/logout/').catch(err => console.error("Logout API call failed", err));
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        setToken(null);
        setUser(mockUser);
        delete apiClient.defaults.headers.common['Authorization'];
    };

    const value = { user, token, isLoading, login, logout };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

// Hook personalizado para acceder fácilmente al contexto de autenticación.
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth debe ser usado dentro de un AuthProvider');
    }
    return context;
};
