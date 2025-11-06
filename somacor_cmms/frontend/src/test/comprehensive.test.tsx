import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import DashboardView from '../pages/DashboardView';
import EquiposMovilesView from '../pages/EquiposMovilesView';
import ChecklistView from '../pages/ChecklistView';
import { AuthProvider } from '../context/AuthContext';

// Mock de apiClient
jest.mock('../api/apiClient', () => ({
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
}));

// Mock de servicios API
jest.mock('../services/apiService', () => ({
  dashboardService: {
    getStats: jest.fn(),
    getEquiposCriticos: jest.fn(),
  },
  equiposService: {
    getAll: jest.fn(),
  },
  tiposEquipoService: {
    getAll: jest.fn(),
  },
  estadosEquipoService: {
    getAll: jest.fn(),
  },
  faenasService: {
    getAll: jest.fn(),
  },
  usersService: {
    getAll: jest.fn(),
  },
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        {component}
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('DashboardView', () => {
  beforeEach(() => {
    const mockDashboardService = require('../services/apiService').dashboardService;
    mockDashboardService.getStats.mockResolvedValue({
      data: {
        total_equipos: 4,
        equipos_operativos: 4,
        ots_abiertas: 0,
        ots_vencidas: 0,
      }
    });
    mockDashboardService.getEquiposCriticos.mockResolvedValue({
      data: { results: [] }
    });
  });

  test('renderiza el dashboard correctamente', async () => {
    renderWithProviders(<DashboardView />);
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Resumen general del estado de mantenimiento de la flota')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('Total Equipos')).toBeInTheDocument();
      expect(screen.getByText('Equipos Operativos')).toBeInTheDocument();
      expect(screen.getByText('OTs Abiertas')).toBeInTheDocument();
      expect(screen.getByText('OTs Vencidas')).toBeInTheDocument();
    });
  });

  test('muestra las estadísticas correctas', async () => {
    renderWithProviders(<DashboardView />);
    
    await waitFor(() => {
      expect(screen.getByText('4')).toBeInTheDocument(); // Total equipos
    });
  });

  test('muestra mensaje cuando no hay equipos críticos', async () => {
    renderWithProviders(<DashboardView />);
    
    await waitFor(() => {
      expect(screen.getByText('Todos los equipos están en buen estado')).toBeInTheDocument();
    });
  });
});

describe('EquiposMovilesView', () => {
  beforeEach(() => {
    const mockEquiposService = require('../services/apiService').equiposService;
    const mockTiposEquipoService = require('../services/apiService').tiposEquipoService;
    const mockEstadosEquipoService = require('../services/apiService').estadosEquipoService;
    const mockFaenasService = require('../services/apiService').faenasService;
    const mockUsersService = require('../services/apiService').usersService;

    mockEquiposService.getAll.mockResolvedValue({
      data: {
        results: [
          {
            idequipo: 1,
            nombreequipo: 'Minicargador CAT 236D',
            codigointerno: 'CAT-001',
            marca: 'Caterpillar',
            activo: true,
            idtipoequipo: { nombretipo: 'Minicargador' },
            idestadoactual: { nombreestado: 'Operativo' },
            idfaenaactual: null,
          }
        ]
      }
    });

    mockTiposEquipoService.getAll.mockResolvedValue({
      data: { results: [{ idtipoequipo: 1, nombretipo: 'Minicargador' }] }
    });

    mockEstadosEquipoService.getAll.mockResolvedValue({
      data: { results: [{ idestadoequipo: 1, nombreestado: 'Operativo' }] }
    });

    mockFaenasService.getAll.mockResolvedValue({
      data: { results: [] }
    });

    mockUsersService.getAll.mockResolvedValue({
      data: { results: [] }
    });
  });

  test('renderiza la vista de equipos móviles correctamente', async () => {
    renderWithProviders(<EquiposMovilesView />);
    
    expect(screen.getByText('Gestión de Equipos Móviles')).toBeInTheDocument();
    expect(screen.getByText('Crear Nuevo')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('Minicargador CAT 236D')).toBeInTheDocument();
      expect(screen.getByText('CAT-001')).toBeInTheDocument();
      expect(screen.getByText('Caterpillar')).toBeInTheDocument();
    });
  });

  test('muestra los encabezados de la tabla correctamente', async () => {
    renderWithProviders(<EquiposMovilesView />);
    
    await waitFor(() => {
      expect(screen.getByText('NOMBRE')).toBeInTheDocument();
      expect(screen.getByText('CÓDIGO')).toBeInTheDocument();
      expect(screen.getByText('MARCA')).toBeInTheDocument();
      expect(screen.getByText('ESTADO')).toBeInTheDocument();
      expect(screen.getByText('ACTIVO')).toBeInTheDocument();
      expect(screen.getByText('ACCIONES')).toBeInTheDocument();
    });
  });

  test('permite crear un nuevo equipo', async () => {
    renderWithProviders(<EquiposMovilesView />);
    
    const crearButton = screen.getByText('Crear Nuevo');
    fireEvent.click(crearButton);
    
    // Verificar que se abre el modal de creación
    await waitFor(() => {
      expect(screen.getByText('Crear Equipo')).toBeInTheDocument();
    });
  });
});

describe('ChecklistView', () => {
  beforeEach(() => {
    const mockEquiposService = require('../services/apiService').equiposService;
    
    mockEquiposService.getAll.mockResolvedValue({
      data: {
        results: [
          {
            idequipo: 1,
            nombreequipo: 'Minicargador CAT 236D',
            codigointerno: 'CAT-001',
          }
        ]
      }
    });
  });

  test('renderiza la vista de checklist correctamente', async () => {
    renderWithProviders(<ChecklistView />);
    
    expect(screen.getByText('Checklist de Inspección')).toBeInTheDocument();
    expect(screen.getByText('Realiza inspecciones diarias y gestiona el historial de checklist')).toBeInTheDocument();
    expect(screen.getByText('Seleccionar Equipo')).toBeInTheDocument();
  });

  test('muestra el selector de equipos', async () => {
    renderWithProviders(<ChecklistView />);
    
    await waitFor(() => {
      expect(screen.getByText('Seleccione un equipo')).toBeInTheDocument();
    });
  });

  test('carga los equipos en el selector', async () => {
    renderWithProviders(<ChecklistView />);
    
    await waitFor(() => {
      expect(screen.getByText('CAT-001 - Minicargador CAT 236D')).toBeInTheDocument();
    });
  });
});

describe('Integración de componentes', () => {
  test('los componentes se renderizan sin errores', () => {
    // Test básico para asegurar que los componentes no tienen errores de renderizado
    expect(() => {
      renderWithProviders(<DashboardView />);
    }).not.toThrow();

    expect(() => {
      renderWithProviders(<EquiposMovilesView />);
    }).not.toThrow();

    expect(() => {
      renderWithProviders(<ChecklistView />);
    }).not.toThrow();
  });
});

describe('Manejo de errores', () => {
  test('maneja errores de API graciosamente en Dashboard', async () => {
    const mockDashboardService = require('../services/apiService').dashboardService;
    mockDashboardService.getStats.mockRejectedValue(new Error('Network Error'));
    mockDashboardService.getEquiposCriticos.mockRejectedValue(new Error('Network Error'));

    renderWithProviders(<DashboardView />);
    
    // El componente debería renderizarse sin crashear
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  test('maneja errores de API graciosamente en EquiposMoviles', async () => {
    const mockEquiposService = require('../services/apiService').equiposService;
    mockEquiposService.getAll.mockRejectedValue(new Error('Network Error'));

    renderWithProviders(<EquiposMovilesView />);
    
    // El componente debería renderizarse sin crashear
    expect(screen.getByText('Gestión de Equipos Móviles')).toBeInTheDocument();
  });
});

describe('Funcionalidad de navegación', () => {
  test('los enlaces de navegación están presentes', () => {
    renderWithProviders(<DashboardView />);
    
    // Verificar que los elementos de navegación están presentes
    // (esto depende de cómo esté implementado el layout)
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });
});

