"""
Cliente HTTP para interactuar con la API del CMMS Somacor v2
"""

import requests
from typing import Dict, List, Optional, Any
from loguru import logger
import sys
from pathlib import Path

# Agregar el directorio config al path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.airflow_config import CMSSConfig, LoggingConfig

# Configurar logging
logger.add(
    LoggingConfig.LOG_FILE,
    format=LoggingConfig.FORMAT,
    level=LoggingConfig.LEVEL,
    rotation=LoggingConfig.ROTATION,
    retention=LoggingConfig.RETENTION
)


class CMSSAPIClient:
    """Cliente para interactuar con la API REST del CMMS"""
    
    def __init__(self, base_url: str = None, api_token: str = None):
        """
        Inicializar cliente de API
        
        Args:
            base_url: URL base de la API (opcional, usa config por defecto)
            api_token: Token de autenticación (opcional, usa config por defecto)
        """
        self.base_url = base_url or CMSSConfig.API_BASE_URL
        self.api_token = api_token or CMSSConfig.API_TOKEN
        self.timeout = CMSSConfig.API_TIMEOUT
        
        self.headers = {
            'Content-Type': 'application/json',
        }
        
        if self.api_token:
            self.headers['Authorization'] = f'Bearer {self.api_token}'
        
        logger.info(f"Cliente API inicializado con base_url: {self.base_url}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Realizar una petición HTTP a la API
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE, PATCH)
            endpoint: Endpoint de la API
            params: Parámetros de query string
            data: Datos del body (form data)
            json: Datos del body (JSON)
        
        Returns:
            Respuesta de la API en formato dict
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Realizando petición {method} a {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                data=data,
                json=json,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            logger.debug(f"Respuesta exitosa: {response.status_code}")
            
            return response.json() if response.content else {}
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP {e.response.status_code}: {e.response.text}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error de conexión: {str(e)}")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout en la petición: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            raise
    
    # ========================================
    # Métodos para Equipos
    # ========================================
    
    def get_equipos(self, params: Optional[Dict] = None) -> List[Dict]:
        """Obtener lista de equipos"""
        logger.info("Obteniendo lista de equipos")
        response = self._make_request('GET', 'equipos/', params=params)
        return response.get('results', response) if isinstance(response, dict) else response
    
    def get_equipo(self, equipo_id: int) -> Dict:
        """Obtener un equipo específico"""
        logger.info(f"Obteniendo equipo ID: {equipo_id}")
        return self._make_request('GET', f'equipos/{equipo_id}/')
    
    def create_equipo(self, data: Dict) -> Dict:
        """Crear un nuevo equipo"""
        logger.info("Creando nuevo equipo")
        return self._make_request('POST', 'equipos/', json=data)
    
    def update_equipo(self, equipo_id: int, data: Dict) -> Dict:
        """Actualizar un equipo"""
        logger.info(f"Actualizando equipo ID: {equipo_id}")
        return self._make_request('PUT', f'equipos/{equipo_id}/', json=data)
    
    # ========================================
    # Métodos para Órdenes de Trabajo
    # ========================================
    
    def get_ordenes_trabajo(self, params: Optional[Dict] = None) -> List[Dict]:
        """Obtener lista de órdenes de trabajo"""
        logger.info("Obteniendo lista de órdenes de trabajo")
        response = self._make_request('GET', 'ordenes-trabajo/', params=params)
        return response.get('results', response) if isinstance(response, dict) else response
    
    def get_orden_trabajo(self, orden_id: int) -> Dict:
        """Obtener una orden de trabajo específica"""
        logger.info(f"Obteniendo orden de trabajo ID: {orden_id}")
        return self._make_request('GET', f'ordenes-trabajo/{orden_id}/')
    
    def create_orden_trabajo(self, data: Dict) -> Dict:
        """Crear una nueva orden de trabajo"""
        logger.info("Creando nueva orden de trabajo")
        return self._make_request('POST', 'ordenes-trabajo/', json=data)
    
    def update_orden_trabajo(self, orden_id: int, data: Dict) -> Dict:
        """Actualizar una orden de trabajo"""
        logger.info(f"Actualizando orden de trabajo ID: {orden_id}")
        return self._make_request('PATCH', f'ordenes-trabajo/{orden_id}/', json=data)
    
    def complete_orden_trabajo(self, orden_id: int, data: Optional[Dict] = None) -> Dict:
        """Completar una orden de trabajo"""
        logger.info(f"Completando orden de trabajo ID: {orden_id}")
        update_data = data or {}
        update_data['idestadoot'] = 3  # Estado: Completada
        return self.update_orden_trabajo(orden_id, update_data)
    
    # ========================================
    # Métodos para Faenas
    # ========================================
    
    def get_faenas(self, params: Optional[Dict] = None) -> List[Dict]:
        """Obtener lista de faenas"""
        logger.info("Obteniendo lista de faenas")
        response = self._make_request('GET', 'faenas/', params=params)
        return response.get('results', response) if isinstance(response, dict) else response
    
    def get_faena(self, faena_id: int) -> Dict:
        """Obtener una faena específica"""
        logger.info(f"Obteniendo faena ID: {faena_id}")
        return self._make_request('GET', f'faenas/{faena_id}/')
    
    # ========================================
    # Métodos para Usuarios/Técnicos
    # ========================================
    
    def get_usuarios(self, params: Optional[Dict] = None) -> List[Dict]:
        """Obtener lista de usuarios"""
        logger.info("Obteniendo lista de usuarios")
        response = self._make_request('GET', 'usuarios/', params=params)
        return response.get('results', response) if isinstance(response, dict) else response
    
    def get_usuario(self, usuario_id: int) -> Dict:
        """Obtener un usuario específico"""
        logger.info(f"Obteniendo usuario ID: {usuario_id}")
        return self._make_request('GET', f'usuarios/{usuario_id}/')
    
    def get_tecnicos(self) -> List[Dict]:
        """Obtener lista de técnicos (usuarios con rol de técnico)"""
        logger.info("Obteniendo lista de técnicos")
        return self.get_usuarios(params={'idrol': 2})  # Rol 2 = Técnico
    
    # ========================================
    # Métodos para Tipos de Equipo
    # ========================================
    
    def get_tipos_equipo(self) -> List[Dict]:
        """Obtener lista de tipos de equipo"""
        logger.info("Obteniendo lista de tipos de equipo")
        response = self._make_request('GET', 'tipos-equipo/')
        return response.get('results', response) if isinstance(response, dict) else response
    
    # ========================================
    # Métodos para Checklists
    # ========================================
    
    def get_checklist_templates(self, params: Optional[Dict] = None) -> List[Dict]:
        """Obtener plantillas de checklist"""
        logger.info("Obteniendo plantillas de checklist")
        response = self._make_request('GET', 'checklist-templates/', params=params)
        return response.get('results', response) if isinstance(response, dict) else response
    
    def get_checklist_instances(self, params: Optional[Dict] = None) -> List[Dict]:
        """Obtener instancias de checklist completadas"""
        logger.info("Obteniendo instancias de checklist")
        response = self._make_request('GET', 'checklist-instance/', params=params)
        return response.get('results', response) if isinstance(response, dict) else response
    
    def get_checklist_instance(self, instance_id: int) -> Dict:
        """Obtener una instancia de checklist específica"""
        logger.info(f"Obteniendo instancia de checklist ID: {instance_id}")
        return self._make_request('GET', f'checklist-instance/{instance_id}/')
    
    # ========================================
    # Métodos para Dashboard y Estadísticas
    # ========================================
    
    def get_dashboard_stats(self) -> Dict:
        """Obtener estadísticas del dashboard"""
        logger.info("Obteniendo estadísticas del dashboard")
        return self._make_request('GET', 'dashboard/stats/')
    
    def get_dashboard_monthly_data(self, params: Optional[Dict] = None) -> Dict:
        """Obtener datos mensuales de órdenes"""
        logger.info("Obteniendo datos mensuales")
        return self._make_request('GET', 'dashboard/monthly_data/', params=params)
    
    def get_dashboard_maintenance_types(self) -> Dict:
        """Obtener distribución de tipos de mantenimiento"""
        logger.info("Obteniendo distribución de tipos de mantenimiento")
        return self._make_request('GET', 'dashboard/maintenance_types/')
    
    # ========================================
    # Métodos para Planes de Mantenimiento Preventivo
    # ========================================
    
    def get_planes_mantenimiento(self, params: Optional[Dict] = None) -> List[Dict]:
        """Obtener planes de mantenimiento preventivo"""
        logger.info("Obteniendo planes de mantenimiento preventivo")
        response = self._make_request('GET', 'planes-mantenimiento/', params=params)
        return response.get('results', response) if isinstance(response, dict) else response


# Instancia singleton del cliente
cmms_client = CMSSAPIClient()


if __name__ == '__main__':
    # Prueba del cliente
    try:
        client = CMSSAPIClient()
        
        # Probar obtener equipos
        equipos = client.get_equipos()
        logger.info(f"Total de equipos: {len(equipos)}")
        
        # Probar obtener órdenes de trabajo
        ordenes = client.get_ordenes_trabajo()
        logger.info(f"Total de órdenes de trabajo: {len(ordenes)}")
        
        # Probar obtener estadísticas
        stats = client.get_dashboard_stats()
        logger.info(f"Estadísticas del dashboard: {stats}")
        
    except Exception as e:
        logger.error(f"Error en prueba del cliente: {str(e)}")

