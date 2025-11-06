// src/pages/AuthPage.tsx
// MODIFICADO: Se ha eliminado completamente el formulario y la lógica de registro.
// La página ahora solo sirve para iniciar sesión, según lo solicitado.

import React, { useState, useContext, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const AuthPage: React.FC = () => {
    // Se mantienen solo los estados necesarios para el login.
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const auth = useContext(AuthContext);
    const navigate = useNavigate();

    // Redirige al dashboard si el usuario ya está autenticado.
    // Aunque el flujo de la app ahora lo evita, es una buena práctica mantenerlo.
    useEffect(() => {
        if (auth?.token) {
            navigate('/dashboard');
        }
    }, [auth, navigate]);

    // Maneja el envío del formulario de inicio de sesión.
    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        try {
            // Llama a la función de login del contexto.
            await auth!.login(username, password);
            // Redirige al dashboard en caso de éxito.
            navigate('/dashboard'); 
        } catch (err: any) {
            setError('Error al iniciar sesión. Verifique sus credenciales.');
            console.error("Login error:", err);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
                <h2 className="text-2xl font-bold text-center text-gray-800">
                    Iniciar Sesión - Somacor CMMS
                </h2>

                <form onSubmit={handleLogin}>
                    {/* Muestra un mensaje de error si ocurre uno. */}
                    {error && <p className="text-sm text-center text-red-500 bg-red-100 p-2 rounded">{error}</p>}
                    
                    <div className="space-y-4">
                        {/* Campo para el nombre de usuario. */}
                        <input 
                            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
                            type="text" 
                            placeholder="Nombre de usuario" 
                            value={username} 
                            onChange={(e) => setUsername(e.target.value)} 
                            required 
                        />
                        {/* Campo para la contraseña. */}
                        <input 
                            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
                            type="password" 
                            placeholder="Contraseña" 
                            value={password} 
                            onChange={(e) => setPassword(e.target.value)} 
                            required 
                        />
                    </div>
                    
                    {/* Botón para enviar el formulario. */}
                    <button type="submit" className="w-full px-4 py-2 mt-6 font-semibold text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition duration-300">
                        Entrar
                    </button>
                </form>

                {/* Se eliminó el texto y el botón para cambiar a la vista de registro. */}
            </div>
        </div>
    );
};

export default AuthPage;
