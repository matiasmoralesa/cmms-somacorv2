// src/App.tsx
// ARCHIVO ACTUALIZADO: Se añaden ErrorBoundary, optimizaciones de rendimiento y sistema de login

import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ErrorBoundary from './components/shared/ErrorBoundary';
import LoadingSpinner from './components/shared/LoadingSpinner';
import { AppLayout } from './components/layout/AppLayout';
import ProtectedRoute from './components/ProtectedRoute';
import { isAuthenticated } from './utils/auth';

// Lazy loading de componentes para mejorar el rendimiento
const DashboardView = React.lazy(() => import('./pages/DashboardView'));
const EstadoMaquinaView = React.lazy(() => import('./pages/EstadoMaquinaView'));
const EquiposMovilesView = React.lazy(() => import('./pages/EquiposMovilesView'));
const CalendarView = React.lazy(() => import('./pages/CalendarView'));
const UnplannedMaintenanceView = React.lazy(() => import('./pages/UnplannedMaintenanceView'));
const ProfilesView = React.lazy(() => import('./pages/ProfilesView'));
const FaenasView = React.lazy(() => import('./pages/FaenasView'));
const TiposEquipoView = React.lazy(() => import('./pages/TiposEquipoView'));
const TiposTareaView = React.lazy(() => import('./pages/TiposTareaView'));
const MaintenanceConfigView = React.lazy(() => import('./pages/MaintenanceConfigView'));
const MaintenanceFormView = React.lazy(() => import('./pages/MaintenanceFormView'));
const PlaceholderPage = React.lazy(() => import('./components/shared/PlaceholderPage'));
const PlanesMantenimientoView = React.lazy(() => import('./pages/PlanesMantenimientoView'));
const OrdenesTrabajoView = React.lazy(() => import('./pages/OrdenesTrabajoView'));
const EjecucionOTView = React.lazy(() => import('./pages/EjecucionOTView'));
const ChecklistDiarioView = React.lazy(() => import('./pages/ChecklistDiarioView'));
const InventarioView = React.lazy(() => import('./pages/InventarioView'));
const TecnicosView = React.lazy(() => import('./pages/TecnicosView'));
const EquipoDetalleView = React.lazy(() => import('./pages/EquipoDetalleView'));
const EquipoEditarView = React.lazy(() => import('./pages/EquipoEditarView'));

// Componentes de autenticación
const LoginView = React.lazy(() => import('./pages/LoginView'));
const AccesoDenegadoView = React.lazy(() => import('./pages/AccesoDenegadoView'));
const RedirectToLogin = React.lazy(() => import('./pages/RedirectToLogin'));

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        {/* Ruta de login */}
        <Route 
          path="/login" 
          element={
            <Suspense fallback={<LoadingSpinner text="Cargando..." />}>
              <LoginView />
            </Suspense>
          } 
        />
        
        {/* Ruta de acceso denegado */}
        <Route 
          path="/acceso-denegado" 
          element={
            <Suspense fallback={<LoadingSpinner text="Cargando..." />}>
              <AccesoDenegadoView />
            </Suspense>
          } 
        />

        {/* Rutas protegidas */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route 
            index 
            element={
              <Suspense fallback={<LoadingSpinner text="Verificando autenticación..." />}>
                <RedirectToLogin />
              </Suspense>
            } 
          />
          
          <Route 
            path="dashboard" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Dashboard..." />}>
                <DashboardView />
              </Suspense>
            } 
          />
          
          <Route path="equipos">
            <Route 
              index 
              element={
                <Suspense fallback={<LoadingSpinner text="Cargando Equipos..." />}>
                  <EquiposMovilesView />
                </Suspense>
              } 
            />
            <Route 
              path=":id" 
              element={
                <Suspense fallback={<LoadingSpinner text="Cargando Detalles..." />}>
                  <EquipoDetalleView />
                </Suspense>
              } 
            />
            <Route 
              path=":id/editar" 
              element={
                <Suspense fallback={<LoadingSpinner text="Cargando Editor..." />}>
                  <EquipoEditarView />
                </Suspense>
              } 
            />
          </Route>
          
          <Route 
            path="mantenimiento-preventivo" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Mantenimiento Preventivo..." />}>
                <PlanesMantenimientoView />
              </Suspense>
            } 
          />
          
          <Route 
            path="inventario" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Inventario..." />}>
                <InventarioView />
              </Suspense>
            } 
          />
          
          <Route 
            path="tecnicos" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Técnicos..." />}>
                <TecnicosView />
              </Suspense>
            } 
          />
          
          <Route 
            path="configuracion" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Configuración..." />}>
                <MaintenanceConfigView />
              </Suspense>
            } 
          />
          
          <Route 
            path="estado-maquina" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Estado de Máquina..." />}>
                <EstadoMaquinaView />
              </Suspense>
            } 
          />
          
          <Route 
            path="equipos-moviles" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Equipos Móviles..." />}>
                <EquiposMovilesView />
              </Suspense>
            } 
          />
          
          <Route 
            path="calendario" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Calendario..." />}>
                <CalendarView />
              </Suspense>
            } 
          />
          
          <Route 
            path="mantenimiento-planificado" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Mantenimiento Planificado..." />}>
                <MaintenanceFormView />
              </Suspense>
            } 
          />
          
          <Route 
            path="mantenimiento-no-planificado" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Reporte de Fallas..." />}>
                <UnplannedMaintenanceView />
              </Suspense>
            } 
          />
          
          {/* Rutas de Órdenes de Trabajo */}
          <Route path="ordenes-trabajo">
            <Route 
              index 
              element={
                <Suspense fallback={<LoadingSpinner text="Cargando Órdenes de Trabajo..." />}>
                  <OrdenesTrabajoView />
                </Suspense>
              } 
            />
            <Route 
              path=":id" 
              element={
                <Suspense fallback={<LoadingSpinner text="Cargando Ejecución de OT..." />}>
                  <EjecucionOTView />
                </Suspense>
              } 
            />
          </Route>
          
          {/* Ruta unificada para Checklist */}
          <Route 
            path="checklist" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Checklist..." />}>
                <ChecklistDiarioView />
              </Suspense>
            } 
          />
          
          {/* Administración */}
          <Route 
            path="admin/perfiles" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Perfiles..." />}>
                <ProfilesView />
              </Suspense>
            } 
          />
          
          <Route 
            path="admin/programas" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Programas de Mantenimiento..." />}>
                <PlanesMantenimientoView />
              </Suspense>
            } 
          />
          
          {/* Mantenedores */}
          <Route 
            path="mantenedores/faenas" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Faenas..." />}>
                <FaenasView />
              </Suspense>
            } 
          />
          
          <Route 
            path="mantenedores/tipos-equipo" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Tipos de Equipo..." />}>
                <TiposEquipoView />
              </Suspense>
            } 
          />
          
          <Route 
            path="mantenedores/tipos-tarea" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Tipos de Tarea..." />}>
                <TiposTareaView />
              </Suspense>
            } 
          />
          
          <Route 
            path="config/mantenimiento" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando Configuración..." />}>
                <MaintenanceConfigView />
              </Suspense>
            } 
          />
          
          <Route 
            path="*" 
            element={
              <Suspense fallback={<LoadingSpinner text="Cargando..." />}>
                <PlaceholderPage title="Página no encontrada" />
              </Suspense>
            } 
          />
        </Route>
      </Routes>
    </ErrorBoundary>
  );
}

export default App;

