// src/components/shared/GenericCRUD.tsx
// ARCHIVO MODIFICADO: Se mejora la función handleSave para filtrar los datos enviados.

import React, { useState, useEffect, useCallback } from 'react';
import { PlusCircle, Edit, Trash2 } from 'lucide-react';
import apiClient from '../../api/apiClient';
import Modal from '../ui/Modal';
import GenericForm from './GenericForm';

const getNestedValue = (obj, path) => {
    if (typeof path === 'function') {
        return path(obj);
    }
    if (typeof path !== 'string') return 'N/A';
    return path.split('.').reduce((acc, part) => acc && acc[part], obj);
};

const GenericCRUD = ({ title, apiEndpoint, columns, formFields, idAccessor, transformItemForEdit }) => {
    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [currentItem, setCurrentItem] = useState(null);
    const [error, setError] = useState('');

    const fetchData = useCallback(async () => {
        setIsLoading(true);
        setError('');
        try {
            const response = await apiClient.get(apiEndpoint);
            setData(response.data.results || response.data);
        } catch (err) {
            setError('No se pudieron cargar los datos. Verifique la conexión y los permisos de la API.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    }, [apiEndpoint]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleCreate = () => {
        setCurrentItem(null);
        setIsModalOpen(true);
    };

    const handleEdit = (item) => {
        const transformedItem = transformItemForEdit ? transformItemForEdit(item) : item;
        setCurrentItem(transformedItem);
        setIsModalOpen(true);
    };

    const handleDelete = async (id) => {
        if (window.confirm('¿Está seguro de que desea eliminar este elemento?')) {
            try {
                // Se asegura que la URL termine con una barra
                await apiClient.delete(`${apiEndpoint}${id}/`);
                fetchData();
            } catch (err) {
                alert('Error al eliminar el elemento.');
                console.error(err);
            }
        }
    };
    
    const handleSave = async (formData) => {
        const method = currentItem ? 'put' : 'post';
        // La URL de actualización ahora incluye la barra final
        const url = currentItem ? `${apiEndpoint}${currentItem[idAccessor]}/` : apiEndpoint;
        
        // --- INICIO DE LA CORRECCIÓN ---
        // Se construye un 'payload' limpio, incluyendo solo los campos definidos en 'formFields'.
        // Esto previene enviar datos extra (como 'id', 'usuarios', etc.) que el backend rechazaría.
        const allowedKeys = formFields.map(f => f.name);
        const payload: Record<string, any> = Object.keys(formData)
            .filter(key => allowedKeys.includes(key))
            .reduce((obj, key) => {
                // Solo se añaden al payload los campos que no son nulos o indefinidos.
                if (formData[key] !== null && formData[key] !== undefined) {
                    obj[key] = formData[key];
                }
                return obj;
            }, {});

        // Si el campo de contraseña está presente pero vacío, se elimina del payload
        // para evitar que se actualice la contraseña a una cadena vacía.
        if (
            Object.prototype.hasOwnProperty.call(payload, 'password') &&
            payload.password === ''
        ) {
            delete payload.password;
        }
        // --- FIN DE LA CORRECCIÓN ---

        try {
            // Se envía el 'payload' filtrado en lugar del 'formData' completo.
            await apiClient[method](url, payload);
            fetchData();
            setIsModalOpen(false);
        } catch (err) {
            const errorData = err.response?.data;
            let errorMessages = 'Revise los datos e intente de nuevo.';
            if (errorData) {
                // Se formatean los errores de validación del backend para mostrarlos en la alerta.
                errorMessages = Object.entries(errorData).map(([field, messages]) => {
                    const messageText = Array.isArray(messages) ? messages.join(', ') : String(messages);
                    return `${field}: ${messageText}`;
                }).join('\n');
            }
            alert(`Error al guardar:\n${errorMessages}`);
            console.error("Error response data:", err.response?.data || err);
        }
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-gray-800">{title}</h1>
                <button onClick={handleCreate} className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center hover:bg-blue-700 shadow-sm transition-colors">
                    <PlusCircle size={20} className="mr-2" />
                    Crear Nuevo
                </button>
            </div>

            {isLoading && <p>Cargando datos...</p>}
            {error && <p className="text-red-500 bg-red-100 p-3 rounded-md">{error}</p>}

            {!isLoading && !error && (
                <div className="bg-white shadow-md rounded-xl overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                {columns.map(col => <th key={col.header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{col.header}</th>)}
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {data.map(item => (
                                <tr key={item[idAccessor]}>
                                    {columns.map(col => (
                                        <td key={`${item[idAccessor]}-${col.accessor}`} className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                                            {typeof getNestedValue(item, col.accessor) === 'boolean'
                                                ? getNestedValue(item, col.accessor) ? 'Sí' : 'No'
                                                : getNestedValue(item, col.accessor) || 'N/A'
                                            }
                                        </td>
                                    ))}
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <button onClick={() => handleEdit(item)} className="text-indigo-600 hover:text-indigo-900 mr-4"><Edit size={18} /></button>
                                        <button onClick={() => handleDelete(item[idAccessor])} className="text-red-600 hover:text-red-900"><Trash2 size={18} /></button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={currentItem ? `Editar ${title}` : `Crear ${title}`}>
                <GenericForm 
                    fields={formFields} 
                    currentItem={currentItem} 
                    onSave={handleSave} 
                    onCancel={() => setIsModalOpen(false)} 
                />
            </Modal>
        </div>
    );
};

export default GenericCRUD;
