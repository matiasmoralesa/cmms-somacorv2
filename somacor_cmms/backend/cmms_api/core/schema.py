"""
API Schema and documentation utilities
"""
from rest_framework.schemas import AutoSchema
from rest_framework.schemas.openapi import AutoSchema as OpenAPISchema
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.openapi import OpenApiParameter
from typing import Dict, Any


class CMMSAutoSchema(OpenAPISchema):
    """
    Custom schema generator for CMMS API
    """
    
    def get_operation(self, path, method):
        """
        Override to add custom operation details
        """
        operation = super().get_operation(path, method)
        
        # Add custom tags based on path
        if '/bot/' in path:
            operation['tags'] = ['Bot Integration']
        elif '/dashboard/' in path:
            operation['tags'] = ['Dashboard']
        elif '/equipos/' in path:
            operation['tags'] = ['Equipment']
        elif '/ordenes/' in path:
            operation['tags'] = ['Work Orders']
        elif '/checklist/' in path:
            operation['tags'] = ['Checklist']
        elif '/mantenimiento/' in path:
            operation['tags'] = ['Maintenance']
        else:
            operation['tags'] = ['General']
        
        # Add security requirements
        if method.lower() != 'options':
            operation['security'] = [{'Token': []}]
        
        return operation


# Common response schemas
class SuccessResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    data = serializers.JSONField()
    timestamp = serializers.FloatField()


class ErrorResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    error = serializers.DictField()
    timestamp = serializers.FloatField()


class PaginatedResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    data = serializers.JSONField()
    pagination = serializers.DictField()
    timestamp = serializers.FloatField()


# Equipment schemas
class EquipmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    patente = serializers.CharField()
    brand = serializers.CharField()
    model = serializers.CharField()
    type = serializers.CharField()
    status = serializers.CharField()
    location = serializers.CharField()
    active = serializers.BooleanField()


class EquipmentSearchSerializer(serializers.Serializer):
    search_term = serializers.CharField(
        help_text="Search term for equipment name, code, or patente"
    )


# Work Order schemas
class WorkOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    number = serializers.CharField()
    equipment_name = serializers.CharField()
    status = serializers.CharField()
    priority = serializers.CharField()
    maintenance_type = serializers.CharField()
    assigned_technician = serializers.CharField()
    created_date = serializers.DateTimeField()


class WorkOrderCreateSerializer(serializers.Serializer):
    equipment_id = serializers.IntegerField(
        help_text="ID of the equipment"
    )
    description = serializers.CharField(
        help_text="Description of the work order"
    )
    priority = serializers.ChoiceField(
        choices=['Baja', 'Media', 'Alta', 'Crítica'],
        default='Media',
        help_text="Priority level"
    )
    maintenance_type = serializers.CharField(
        default='Correctivo',
        help_text="Type of maintenance"
    )
    reported_by = serializers.CharField(
        required=False,
        help_text="Name of the person reporting"
    )


# Dashboard schemas
class DashboardStatsSerializer(serializers.Serializer):
    ordenes_activas = serializers.IntegerField()
    equipos_totales = serializers.IntegerField()
    tecnicos_disponibles = serializers.IntegerField()
    repuestos_criticos = serializers.IntegerField()
    ordenes_urgentes = serializers.IntegerField()
    equipos_operativos = serializers.IntegerField()
    tecnicos_totales = serializers.IntegerField()


# Bot integration schemas
class BotWebhookSerializer(serializers.Serializer):
    event_type = serializers.CharField(
        help_text="Type of event from bot system"
    )
    data = serializers.DictField(
        help_text="Event data payload"
    )


# Common decorators
def cmms_api_view(
    operation_id: str = None,
    summary: str = None,
    description: str = None,
    tags: list = None,
    responses: Dict[int, Any] = None
):
    """
    Decorator for CMMS API views with standardized documentation
    """
    def decorator(func):
        return extend_schema(
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags or ['CMMS API'],
            responses=responses or {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            }
        )(func)
    return decorator


def bot_api_view(
    operation_id: str = None,
    summary: str = None,
    description: str = None,
    responses: Dict[int, Any] = None
):
    """
    Decorator for Bot integration API views
    """
    def decorator(func):
        return extend_schema(
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=['Bot Integration'],
            responses=responses or {
                200: SuccessResponseSerializer,
                400: ErrorResponseSerializer,
                401: ErrorResponseSerializer,
                403: ErrorResponseSerializer,
                404: ErrorResponseSerializer,
                500: ErrorResponseSerializer,
            }
        )(func)
    return decorator


# API Info
API_INFO = {
    'title': 'Somacor CMMS API',
    'description': '''
    # Somacor CMMS API
    
    Sistema de Gestión de Mantenimiento Computarizado (CMMS) para Somacor.
    
    ## Características
    
    - **Gestión de Equipos**: Administración completa de equipos móviles
    - **Órdenes de Trabajo**: Creación y seguimiento de mantenimientos
    - **Checklists**: Sistema de inspecciones y verificaciones
    - **Mantenimiento Preventivo**: Programación y seguimiento
    - **Integración Bot**: APIs especializadas para bot omnicanal
    - **Dashboard**: Estadísticas y métricas en tiempo real
    
    ## Autenticación
    
    La API utiliza autenticación por token. Incluye el header:
    ```
    Authorization: Token <your_token>
    ```
    
    ## Versionado
    
    La API está versionada. La versión actual es v1:
    - Endpoints legacy: `/api/`
    - Endpoints v1: `/api/v1/`
    
    ## Bot Integration
    
    Para integración con el bot omnicanal, utiliza los endpoints bajo `/api/v1/bot/`
    con el header `X-Bot-Token: <bot_token>`.
    ''',
    'version': '1.0.0',
    'contact': {
        'name': 'Somacor CMMS Team',
        'email': 'cmms@somacor.com',
    },
    'license': {
        'name': 'Proprietary',
    },
}
