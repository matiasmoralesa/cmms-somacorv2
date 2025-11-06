import React from 'react';

const PlaceholderPage = ({ title }) => (
    <div>
        <h1 className="text-3xl font-bold text-gray-800 mb-8">{title}</h1>
        <div className="bg-white p-6 rounded-xl shadow-md">
            <p>Contenido para la sección de {title} se desarrollará aquí.</p>
        </div>
    </div>
);

export default PlaceholderPage;
