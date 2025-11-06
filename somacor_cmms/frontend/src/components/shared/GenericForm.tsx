import React, { useState, useEffect } from 'react';
import apiClient from '../../api/apiClient';

/**
 * Componente de formulario reutilizable para crear y editar registros.
 */
const GenericForm = ({ fields, currentItem, onSave, onCancel }) => {
    const [formData, setFormData] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        // Inicializa el estado del formulario.
        // Si `currentItem` existe (modo edición), rellena el formulario con sus datos.
        // Si no (modo creación), usa los valores por defecto definidos en `fields`.
        const initialData = fields.reduce((acc, field) => {
            if (currentItem) {
                // [CORREGIDO] Maneja correctamente los campos de relación (ej: idfaenaactual).
                // Si el valor es un objeto (como {idfaena: 1, nombrefaena: '...'}),
                // extrae solo el ID para el campo del formulario.
                const value = currentItem[field.name];
                if (field.type === 'select' && typeof value === 'object' && value !== null) {
                    // Busca la clave primaria en el objeto anidado (ej: 'idfaena' en el objeto de 'idfaenaactual')
                    const primaryKey = Object.keys(value).find(k => k.startsWith('id'));
                    acc[field.name] = primaryKey ? value[primaryKey] : null;
                } else {
                    acc[field.name] = value;
                }
            } else {
                // Para creación, usa el valor por defecto o un valor vacío.
                acc[field.name] = field.defaultValue ?? (field.type === 'checkbox' ? false : '');
            }
            return acc;
        }, {});
        setFormData(initialData);
        setLoading(false);
    }, [fields, currentItem]);
    
    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');
        // Limpia los valores vacíos para que no se envíen a la API si no son requeridos
        const cleanedData = Object.fromEntries(
            Object.entries(formData).filter(([_, v]) => v !== null && v !== '')
        );
        onSave(cleanedData);
    };

    if (loading) return <p>Cargando formulario...</p>;

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            {fields.map(field => (
                <div key={field.name}>
                    <label htmlFor={field.name} className="block text-sm font-medium text-gray-700">{field.label}</label>
                    {field.type === 'select' ? (
                        <select
                            name={field.name}
                            id={field.name}
                            value={formData[field.name] || ''}
                            onChange={handleChange}
                            required={field.required !== false}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                            <option value="">-- Seleccione --</option>
                            {field.options?.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                        </select>
                    ) : field.type === 'checkbox' ? (
                        <input
                            type="checkbox"
                            name={field.name}
                            id={field.name}
                            checked={formData[field.name] || false}
                            onChange={handleChange}
                            className="mt-1 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                        />
                    ) : (
                        <input
                            type={field.type || 'text'}
                            name={field.name}
                            id={field.name}
                            value={formData[field.name] || ''}
                            onChange={handleChange}
                            required={field.required !== false}
                            placeholder={field.placeholder || ''}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                        />
                    )}
                </div>
            ))}
            <div className="flex justify-end pt-6 space-x-3">
                <button type="button" onClick={onCancel} className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300">Cancelar</button>
                <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">Guardar</button>
            </div>
        </form>
    );
};

export default GenericForm;
