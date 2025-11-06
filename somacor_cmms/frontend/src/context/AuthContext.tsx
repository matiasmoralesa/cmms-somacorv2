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

// Eliminado el mockUser para forzar autenticación real

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    // El estado del usuario se inicializa como null para forzar autenticación real
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem('authToken'));
    // isLoading se establece en 'true' inicialmente para verificar autenticación
    const [isLoading, setIsLoading] = useState(true);

    // useEffect para verificar autenticación al cargar la aplicación
    useEffect(() => {
        const storedToken = localStorage.getItem('authToken');
        const storedUser = localStorage.getItem('userInfo');

        if (storedToken && storedUser) {
            try {
                // Si hay un usuario real en localStorage, se usa.
                const parsedUser: User = JSON.parse(storedUser);
                setUser(parsedUser);
                setToken(storedToken);
                apiClient.defaults.headers.common['Authorization'] = `Token ${storedToken}`;
            } catch (error) {
                // Si falla la carga, limpiar datos y forzar login
                localStorage.removeItem('authToken');
                localStorage.removeItem('userInfo');
                localStorage.removeItem('userRole');
                setUser(null);
                setToken(null);
            }
        } else {
            // No hay datos de autenticación, asegurar que esté limpio
            setUser(null);
            setToken(null);
        }
        setIsLoading(false);
    }, []);

    // Función de login que maneja la autenticación real
    const login = async (username: string, password: string) => {
        const response = await apiClient.post<{ token: string; user: User; rol: any }>('/login/', { username, password });
        const { token: newToken, user: newUser, rol } = response.data;
        
        // Guardar datos en localStorage
        localStorage.setItem('authToken', newToken);
        localStorage.setItem('userInfo', JSON.stringify(newUser));
        localStorage.setItem('userRole', JSON.stringify(rol));
        
        // Actualizar estado
        setToken(newToken);
        setUser(newUser);
        apiClient.defaults.headers.common['Authorization'] = `Token ${newToken}`;
    };

    // Al cerrar sesión, limpiar todo y redireccionar al login
    const logout = () => {
        apiClient.post('/logout/').catch(err => console.error("Logout API call failed", err));
        localStorage.removeItem('authToken');
        localStorage.removeItem('userInfo');
        localStorage.removeItem('userRole');
        setToken(null);
        setUser(null);
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
