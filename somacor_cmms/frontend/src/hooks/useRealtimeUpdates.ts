import { useEffect, useState, useCallback } from 'react';
import { useWebSocket } from './useWebSocket';

interface Notification {
  id: string;
  type: 'success' | 'info' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: number;
  read: boolean;
}

interface RealtimeData {
  dashboard?: any;
  equipos?: any;
  ordenes?: any;
}

interface UseRealtimeUpdatesOptions {
  onNotification?: (notification: Notification) => void;
  onDataUpdate?: (dataType: string, data: any) => void;
}

interface UseRealtimeUpdatesReturn {
  notifications: Notification[];
  realtimeData: RealtimeData;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  isConnected: boolean;
  markNotificationAsRead: (id: string) => void;
  clearNotifications: () => void;
  subscribeToUpdates: (type: 'dashboard' | 'equipos' | 'ordenes') => void;
}

export const useRealtimeUpdates = ({
  onNotification,
  onDataUpdate
}: UseRealtimeUpdatesOptions = {}): UseRealtimeUpdatesReturn => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [realtimeData, setRealtimeData] = useState<RealtimeData>({});
  
  // Get auth token for WebSocket connection
  const getAuthToken = () => {
    return localStorage.getItem('authToken');
  };

  // WebSocket URLs
  const wsUrls = {
    dashboard: `ws://localhost:8000/ws/dashboard/?token=${getAuthToken()}`,
    equipos: `ws://localhost:8000/ws/equipos/?token=${getAuthToken()}`,
    ordenes: `ws://localhost:8000/ws/ordenes/?token=${getAuthToken()}`,
    notifications: `ws://localhost:8000/ws/notifications/?token=${getAuthToken()}`
  };

  // Check if WebSockets are supported
  const isWebSocketSupported = typeof WebSocket !== 'undefined';
  
  // TEMPORAL: Disable WebSockets to prevent infinite loop errors
  const websocketsEnabled = false; // Set to true when WebSocket backend is ready
  
  // Log WebSocket status
  useEffect(() => {
    if (!websocketsEnabled) {
      console.log('🔌 [WEBSOCKETS] Deshabilitados temporalmente para evitar errores de bucle infinito');
    }
  }, [websocketsEnabled]);

  // Handle WebSocket messages
  const handleMessage = useCallback((message: any) => {
    console.log('WebSocket message received:', message);

    switch (message.type) {
      case 'notification':
        const notification: Notification = {
          id: `notif_${Date.now()}_${Math.random()}`,
          type: message.data.event_type === 'work_order_created' ? 'success' : 
                message.data.event_type === 'work_order_completed' ? 'success' :
                message.data.event_type === 'equipment_status_changed' ? 'warning' : 'info',
          title: getNotificationTitle(message.data.event_type),
          message: getNotificationMessage(message.data.event_type, message.data.data),
          timestamp: message.data.timestamp * 1000,
          read: false
        };
        
        setNotifications(prev => [notification, ...prev.slice(0, 49)]); // Keep last 50 notifications
        onNotification?.(notification);
        break;

      case 'data_update':
        const { data_type, data } = message.data;
        setRealtimeData(prev => ({
          ...prev,
          [data_type.replace('_update', '')]: data
        }));
        onDataUpdate?.(data_type, data);
        break;

      case 'dashboard_data':
        setRealtimeData(prev => ({
          ...prev,
          dashboard: message.data
        }));
        break;

      case 'equipos_data':
        setRealtimeData(prev => ({
          ...prev,
          equipos: message.data
        }));
        break;

      case 'ordenes_data':
        setRealtimeData(prev => ({
          ...prev,
          ordenes: message.data
        }));
        break;

      default:
        console.log('Unknown message type:', message.type);
    }
  }, [onNotification, onDataUpdate]);

  // WebSocket connections (only if supported and enabled)
  const dashboardWs = useWebSocket({
    url: (isWebSocketSupported && websocketsEnabled) ? wsUrls.dashboard : '',
    onMessage: handleMessage,
    onError: (error) => console.error('Dashboard WebSocket error:', error),
    maxReconnectAttempts: 3
  });

  const equiposWs = useWebSocket({
    url: (isWebSocketSupported && websocketsEnabled) ? wsUrls.equipos : '',
    onMessage: handleMessage,
    onError: (error) => console.error('Equipos WebSocket error:', error),
    maxReconnectAttempts: 3
  });

  const ordenesWs = useWebSocket({
    url: (isWebSocketSupported && websocketsEnabled) ? wsUrls.ordenes : '',
    onMessage: handleMessage,
    onError: (error) => console.error('Ordenes WebSocket error:', error),
    maxReconnectAttempts: 3
  });

  const notificationsWs = useWebSocket({
    url: (isWebSocketSupported && websocketsEnabled) ? wsUrls.notifications : '',
    onMessage: handleMessage,
    onError: (error) => console.error('Notifications WebSocket error:', error),
    maxReconnectAttempts: 3
  });

  // Subscribe to updates
  const subscribeToUpdates = useCallback((type: 'dashboard' | 'equipos' | 'ordenes') => {
    const ws = type === 'dashboard' ? dashboardWs : 
               type === 'equipos' ? equiposWs : ordenesWs;
    
    if (ws.isConnected) {
      ws.sendMessage({ type: 'subscribe' });
    }
  }, [dashboardWs, equiposWs, ordenesWs]);

  // Mark notification as read
  const markNotificationAsRead = useCallback((id: string) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === id ? { ...notif, read: true } : notif
      )
    );
  }, []);

  // Clear all notifications
  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Auto-subscribe when connected
  useEffect(() => {
    if (dashboardWs.isConnected) {
      subscribeToUpdates('dashboard');
    }
  }, [dashboardWs.isConnected, subscribeToUpdates]);

  useEffect(() => {
    if (equiposWs.isConnected) {
      subscribeToUpdates('equipos');
    }
  }, [equiposWs.isConnected, subscribeToUpdates]);

  useEffect(() => {
    if (ordenesWs.isConnected) {
      subscribeToUpdates('ordenes');
    }
  }, [ordenesWs.isConnected, subscribeToUpdates]);

  // Determine overall connection status
  const connectionStatus = dashboardWs.isConnected && equiposWs.isConnected && 
                          ordenesWs.isConnected && notificationsWs.isConnected 
                          ? 'connected' : 'disconnected';

  const isConnected = dashboardWs.isConnected || equiposWs.isConnected || 
                     ordenesWs.isConnected || notificationsWs.isConnected;

  return {
    notifications,
    realtimeData,
    connectionStatus,
    isConnected,
    markNotificationAsRead,
    clearNotifications,
    subscribeToUpdates
  };
};

// Helper functions
function getNotificationTitle(eventType: string): string {
  switch (eventType) {
    case 'work_order_created':
      return 'Nueva Orden de Trabajo';
    case 'work_order_updated':
      return 'Orden de Trabajo Actualizada';
    case 'work_order_completed':
      return 'Orden de Trabajo Completada';
    case 'equipment_status_changed':
      return 'Estado de Equipo Cambiado';
    case 'checklist_completed':
      return 'Checklist Completado';
    default:
      return 'Actualización del Sistema';
  }
}

function getNotificationMessage(eventType: string, data: any): string {
  switch (eventType) {
    case 'work_order_created':
      return `Nueva orden de trabajo ${data.work_order_number} creada para ${data.equipment_name}`;
    case 'work_order_updated':
      return `Orden de trabajo ${data.work_order_number} actualizada`;
    case 'work_order_completed':
      return `Orden de trabajo ${data.work_order_number} completada`;
    case 'equipment_status_changed':
      return `Estado del equipo ${data.equipment_name} cambiado a ${data.new_status}`;
    case 'checklist_completed':
      return `Checklist completado para ${data.equipment_name}`;
    default:
      return 'Se ha producido una actualización en el sistema';
  }
}
