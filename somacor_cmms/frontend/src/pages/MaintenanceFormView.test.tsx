import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MaintenanceFormView from '@/pages/MaintenanceFormView';
import { AuthProvider } from "@/context/AuthContext";
import { BrowserRouter as Router } from "react-router-dom";
import * as apiService from '@/services/apiService';
import apiClient from '@/api/apiClient';

// Mock de los servicios de API
jest.mock("@/services/apiService");
jest.mock("@/api/apiClient");

const mockEquipos = [
  { idequipo: 1, nombreequipo: 'Equipo 1', codigointerno: 'EQ001', idtipoequipo: 101 },
];

const mockPlanes = [
  { idplanmantenimiento: 1, nombreplan: 'Plan A', idtipoequipo: 101, detalles: [{ intervalohorasoperacion: 100 }] },
];

const mockTecnicos = [
  { id: 1, username: 'tecnico1', first_name: 'Juan', last_name: 'Perez' },
];

describe('MaintenanceFormView', () => {
  beforeEach(() => {
    // Resetear mocks antes de cada prueba
    jest.clearAllMocks();

    // Configurar mocks para las llamadas a la API
    (apiService.equiposService.getAll as jest.Mock).mockResolvedValue({ results: mockEquipos });
    (apiService.planesMantenimientoService.getAll as jest.Mock).mockResolvedValue({ results: mockPlanes });
    (apiService.userService.getAll as jest.Mock).mockResolvedValue({ results: mockTecnicos });
    (apiClient.post as jest.Mock).mockResolvedValue({});
  });

  const renderComponent = () => {
    act(() => {
      render(
        <Router>
          <AuthProvider>
            <MaintenanceFormView />
          </AuthProvider>
        </Router>
      );
    });
  };

  test("carga y muestra los equipos, planes y técnicos", async () => {
    await renderComponent();

    expect(screen.getByText('Cargando...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByLabelText(/Seleccione el Equipo/i)).toBeInTheDocument();
    });

    expect(screen.getByRole('option', { name: /-- Elija un equipo --/i })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /Equipo 1/i })).toBeInTheDocument();
  });

  test("permite seleccionar un equipo y muestra los planes de mantenimiento relevantes", async () => {
    await renderComponent();

    await waitFor(() => {
      expect(screen.getByLabelText(/Seleccione el Equipo/i)).toBeInTheDocument();
    });

    const equipoSelect = screen.getByLabelText(/Seleccione el Equipo/i);
    userEvent.selectOptions(equipoSelect, '1'); // Seleccionar Equipo 1

    await waitFor(() => {
      expect(screen.getByLabelText(/Seleccione el Programa de Mantenimiento/i)).toBeInTheDocument();
    });

    expect(screen.getByRole('option', { name: /Plan A/i })).toBeInTheDocument();
  });

  test('permite seleccionar un plan y muestra los intervalos relevantes', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByLabelText(/Seleccione el Equipo/i)).toBeInTheDocument();
    });

    const equipoSelect = screen.getByLabelText(/Seleccione el Equipo/i);
    userEvent.selectOptions(equipoSelect, '1');

    await waitFor(() => {
      expect(screen.getByLabelText(/Seleccione el Programa de Mantenimiento/i)).toBeInTheDocument();
    });

    const planSelect = screen.getByLabelText(/Seleccione el Programa de Mantenimiento/i);
    userEvent.selectOptions(planSelect, '1'); // Seleccionar Plan A

    await waitFor(() => {
      expect(screen.getByLabelText(/Seleccione la Pauta a Ejecutar/i)).toBeInTheDocument();
    });

    expect(screen.getByRole('option', { name: /PM \(100 HRS\)/i })).toBeInTheDocument();
  });

  test('permite enviar el formulario y muestra mensaje de éxito', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByLabelText(/Seleccione el Equipo/i)).toBeInTheDocument();
    });

    userEvent.selectOptions(screen.getByLabelText(/Seleccione el Equipo/i), '1');
    await waitFor(() => screen.getByLabelText(/Seleccione el Programa de Mantenimiento/i));
    userEvent.selectOptions(screen.getByLabelText(/Seleccione el Programa de Mantenimiento/i), '1');
    await waitFor(() => screen.getByLabelText(/Seleccione la Pauta a Ejecutar/i));
    userEvent.selectOptions(screen.getByLabelText(/Seleccione la Pauta a Ejecutar/i), '100');
    userEvent.selectOptions(screen.getByLabelText(/Asignar Técnico Principal/i), '1');
    userEvent.type(screen.getByLabelText(/Fecha de Ejecución Programada/i), '2025-12-31');

    userEvent.click(screen.getByRole('button', { name: /Generar Orden de Trabajo/i }));

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith(
        'ordenes-trabajo/crear-desde-plan/',
        expect.objectContaining({
          idequipo: 1,
          idplanorigen: 1,
          horometro: 100,
          idtecnicoasignado: 1,
          fechaejecucion: '2025-12-31',
        })
      );
    });

    expect(screen.getByText('¡Orden de Trabajo creada exitosamente desde el programa!')).toBeInTheDocument();
  });

  test('muestra mensaje de error si faltan campos', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByLabelText(/Seleccione el Equipo/i)).toBeInTheDocument();
    });

    userEvent.click(screen.getByRole('button', { name: /Generar Orden de Trabajo/i }));

    await waitFor(() => {
      expect(screen.getByText(/Por favor, complete todos los campos/i)).toBeInTheDocument();
    });
  });
});


