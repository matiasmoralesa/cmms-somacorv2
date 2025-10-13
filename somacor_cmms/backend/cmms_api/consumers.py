"""
WebSocket consumers for real-time updates
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .models import OrdenesTrabajo, Equipos
from .core.events import EventManager

logger = logging.getLogger(__name__)


class BaseConsumer(AsyncWebsocketConsumer):
    """
    Base consumer with common functionality
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join user-specific group
        self.user_group = f"user_{self.user.id}"
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected for user {self.user.username}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )
        logger.info(f"WebSocket disconnected for user {self.user.username if hasattr(self, 'user') else 'unknown'}")
    
    async def send_notification(self, event):
        """Send notification to user"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data']
        }))
    
    async def send_data_update(self, event):
        """Send data update to user"""
        await self.send(text_data=json.dumps({
            'type': 'data_update',
            'data': event['data']
        }))


class DashboardConsumer(BaseConsumer):
    """
    Consumer for dashboard real-time updates
    """
    
    async def connect(self):
        await super().connect()
        
        # Join dashboard group
        self.dashboard_group = "dashboard_updates"
        await self.channel_layer.group_add(
            self.dashboard_group,
            self.channel_name
        )
    
    async def disconnect(self, close_code):
        if hasattr(self, 'dashboard_group'):
            await self.channel_layer.group_discard(
                self.dashboard_group,
                self.channel_name
            )
        await super().disconnect(close_code)
    
    async def receive(self, text_data):
        """Handle messages from client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Send initial dashboard data
                dashboard_data = await self.get_dashboard_data()
                await self.send(text_data=json.dumps({
                    'type': 'dashboard_data',
                    'data': dashboard_data
                }))
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from WebSocket")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    @database_sync_to_async
    def get_dashboard_data(self):
        """Get current dashboard data"""
        try:
            from .views_dashboard import dashboard_stats, dashboard_recent_work_orders, dashboard_monthly_data, dashboard_maintenance_types
            
            # This is a simplified version - in production you'd want to call the actual view functions
            return {
                'timestamp': timezone.now().isoformat(),
                'message': 'Dashboard data updated'
            }
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {'error': 'Failed to get dashboard data'}


class EquiposConsumer(BaseConsumer):
    """
    Consumer for equipment real-time updates
    """
    
    async def connect(self):
        await super().connect()
        
        # Join equipos group
        self.equipos_group = "equipos_updates"
        await self.channel_layer.group_add(
            self.equipos_group,
            self.channel_name
        )
    
    async def disconnect(self, close_code):
        if hasattr(self, 'equipos_group'):
            await self.channel_layer.group_discard(
                self.equipos_group,
                self.channel_name
            )
        await super().disconnect(close_code)
    
    async def receive(self, text_data):
        """Handle messages from client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Send initial equipment data
                equipos_data = await self.get_equipos_data()
                await self.send(text_data=json.dumps({
                    'type': 'equipos_data',
                    'data': equipos_data
                }))
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from WebSocket")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    @database_sync_to_async
    def get_equipos_data(self):
        """Get current equipment data"""
        try:
            equipos = Equipos.objects.select_related('idtipoequipo', 'idestadoactual', 'idfaenaactual')[:10]
            return {
                'equipos': [
                    {
                        'id': equipo.idequipo,
                        'nombre': equipo.nombreequipo,
                        'codigo': equipo.codigointerno,
                        'estado': equipo.idestadoactual.nombreestado,
                        'tipo': equipo.idtipoequipo.nombretipo,
                        'ubicacion': equipo.idfaenaactual.nombrefaena if equipo.idfaenaactual else None,
                        'activo': equipo.activo
                    }
                    for equipo in equipos
                ],
                'timestamp': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting equipos data: {e}")
            return {'error': 'Failed to get equipos data'}


class OrdenesConsumer(BaseConsumer):
    """
    Consumer for work orders real-time updates
    """
    
    async def connect(self):
        await super().connect()
        
        # Join ordenes group
        self.ordenes_group = "ordenes_updates"
        await self.channel_layer.group_add(
            self.ordenes_group,
            self.channel_name
        )
    
    async def disconnect(self, close_code):
        if hasattr(self, 'ordenes_group'):
            await self.channel_layer.group_discard(
                self.ordenes_group,
                self.channel_name
            )
        await super().disconnect(close_code)
    
    async def receive(self, text_data):
        """Handle messages from client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Send initial work orders data
                ordenes_data = await self.get_ordenes_data()
                await self.send(text_data=json.dumps({
                    'type': 'ordenes_data',
                    'data': ordenes_data
                }))
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from WebSocket")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    @database_sync_to_async
    def get_ordenes_data(self):
        """Get current work orders data"""
        try:
            ordenes = OrdenesTrabajo.objects.select_related(
                'idequipo', 'idestadoot', 'idtipomantenimientoot', 'idtecnicoasignado'
            ).order_by('-fechacreacionot')[:10]
            
            return {
                'ordenes': [
                    {
                        'id': orden.idordentrabajo,
                        'numero': orden.numeroot,
                        'equipo': orden.idequipo.nombreequipo,
                        'estado': orden.idestadoot.nombreestadoot,
                        'prioridad': orden.prioridad,
                        'tipo': orden.idtipomantenimientoot.nombretipomantenimientoot,
                        'asignado_a': orden.idtecnicoasignado.username if orden.idtecnicoasignado else None,
                        'fecha_creacion': orden.fechacreacionot.isoformat()
                    }
                    for orden in ordenes
                ],
                'timestamp': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting ordenes data: {e}")
            return {'error': 'Failed to get ordenes data'}


class NotificationConsumer(BaseConsumer):
    """
    Consumer for general notifications
    """
    
    async def connect(self):
        await super().connect()
        
        # Join notifications group
        self.notifications_group = "notifications"
        await self.channel_layer.group_add(
            self.notifications_group,
            self.channel_name
        )
    
    async def disconnect(self, close_code):
        if hasattr(self, 'notifications_group'):
            await self.channel_layer.group_discard(
                self.notifications_group,
                self.channel_name
            )
        await super().disconnect(close_code)
    
    async def receive(self, text_data):
        """Handle messages from client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_read':
                # Mark notification as read
                notification_id = data.get('notification_id')
                await self.mark_notification_read(notification_id)
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from WebSocket")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        # This would be implemented with a notifications model
        pass
