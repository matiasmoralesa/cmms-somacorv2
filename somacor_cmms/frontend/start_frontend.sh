#!/bin/bash

# Script de inicio para el frontend de CMMS Somacor v2
# Este script configura y ejecuta el servidor de desarrollo de Vite

echo "===================================="
echo "CMMS Somacor v2 - Frontend Startup"
echo "===================================="
echo ""

# Directorio del proyecto
cd "$(dirname "$0")"

# Verificar que Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "✗ Node.js no está instalado"
    exit 1
fi

echo "✓ Node.js encontrado: $(node --version)"
echo "✓ npm encontrado: $(npm --version)"

# Verificar que las dependencias están instaladas
if [ ! -d "node_modules" ]; then
    echo ""
    echo "⚠ Dependencias no instaladas. Instalando..."
    npm install
else
    echo "✓ Dependencias verificadas"
fi

# Verificar archivo .env
if [ -f .env ]; then
    echo "✓ Archivo .env encontrado"
    echo ""
    echo "Configuración:"
    cat .env | grep -v '^#' | grep -v '^$'
else
    echo "⚠ Archivo .env no encontrado"
fi

echo ""
echo "===================================="
echo "Iniciando servidor de desarrollo..."
echo "===================================="
echo "URL: http://localhost:5173"
echo "API Backend: $(grep VITE_API_BASE_URL .env | cut -d '=' -f2)"
echo "===================================="
echo ""

# Iniciar servidor de desarrollo
npm run dev

