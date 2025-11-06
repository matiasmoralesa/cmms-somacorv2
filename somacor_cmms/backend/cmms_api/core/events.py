"""
Event system for CMMS API to support bot integration and real-time notifications
"""
import logging
from typing import Dict, Any, Callable, List
from django.dispatch import Signal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from cmms_api.models import OrdenesTrabajo, Equipos, ChecklistInstance
import json
import time

logger = logging.getLogger(__name__)

# Define custom signals
work_order_created = Signal()
work_order_updated = Signal()
work_order_completed = Signal()
equipment_status_changed = Signal()
checklist_completed = Signal()
maintenance_scheduled = Signal()

# Event handlers registry
event_handlers: Dict[str, List[Callable]] = {}


class EventManager:
    """
    Centralized event management system
    """
    
    @staticmethod
    def register_handler(event_type: str, handler: Callable):
        """
        Register an event handler
        """
        if event_type not in event_handlers:
            event_handlers[event_type] = []
        event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for event: {event_type}")
    
    @staticmethod
    def emit_event(event_type: str, data: Dict[str, Any]):
        """
        Emit an event to all registered handlers
        """
        if event_type in event_handlers:
            for handler in event_handlers[event_type]:
                try:
                    handler(event_type, data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
        else:
            logger.warning(f"No handlers registered for event: {event_type}")
    
    @staticmethod
    def create_webhook_payload(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create standardized webhook payload
        """
        return {
            'event_type': event_type,
            'timestamp': time.time(),
            'data': data,
            'source': 'cmms_api'
        }


# Bot integration event handlers
def bot_notification_handler(event_type: str, data: Dict[str, Any]):
    """
    Handler to send notifications to bot system
    """
    try:
        # Create webhook payload
        payload = EventManager.create_webhook_payload(event_type, data)
        
        # Send to bot webhook endpoint
        # This would be implemented based on your bot architecture
        logger.info(f"Sending bot notification for {event_type}: {payload}")
        
        # Example: Send to bot webhook
        # requests.post('http://bot-api/webhook', json=payload)
        
    except Exception as e:
        logger.error(f"Error sending bot notification: {e}")


def audit_log_handler(event_type: str, data: Dict[str, Any]):
    """
    Handler to log events for audit purposes
    """
    logger.info(f"Audit Event: {event_type} - {json.dumps(data)}")


def websocket_notification_handler(event_type: str, data: Dict[str, Any]):
    """
    Handler to send WebSocket notifications
    """
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.warning("Channel layer not configured, using fallback")
            from .websocket_fallback import WebSocketFallback
            WebSocketFallback.send_notification("all", event_type, data)
            return
        
        # Send to dashboard group
        async_to_sync(channel_layer.group_send)(
            "dashboard_updates",
            {
                'type': 'send_data_update',
                'data': {
                    'data_type': 'dashboard_update',
                    'event_type': event_type,
                    'timestamp': time.time(),
                    'data': data
                }
            }
        )
        
        # Send to specific groups based on event type
        if event_type in ['work_order_created', 'work_order_updated', 'work_order_completed']:
            async_to_sync(channel_layer.group_send)(
                "ordenes_updates",
                {
                    'type': 'send_data_update',
                    'data': {
                        'data_type': 'ordenes_update',
                        'event_type': event_type,
                        'timestamp': time.time(),
                        'data': data
                    }
                }
            )
        
        if event_type == 'equipment_status_changed':
            async_to_sync(channel_layer.group_send)(
                "equipos_updates",
                {
                    'type': 'send_data_update',
                    'data': {
                        'data_type': 'equipos_update',
                        'event_type': event_type,
                        'timestamp': time.time(),
                        'data': data
                    }
                }
            )
        
        # Send general notification
        async_to_sync(channel_layer.group_send)(
            "notifications",
            {
                'type': 'send_notification',
                'data': {
                    'event_type': event_type,
                    'timestamp': time.time(),
                    'data': data
                }
            }
        )
        
        logger.info(f"WebSocket notifications sent for {event_type}")
        
    except Exception as e:
        logger.error(f"Error sending WebSocket notifications: {e}")
        # Use fallback when Redis is not available
        try:
            from .websocket_fallback import WebSocketFallback
            WebSocketFallback.send_notification("all", event_type, data)
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")


# Register default handlers
EventManager.register_handler('work_order_created', bot_notification_handler)
EventManager.register_handler('work_order_updated', bot_notification_handler)
EventManager.register_handler('work_order_completed', bot_notification_handler)
EventManager.register_handler('equipment_status_changed', bot_notification_handler)
EventManager.register_handler('checklist_completed', bot_notification_handler)

EventManager.register_handler('work_order_created', audit_log_handler)
EventManager.register_handler('work_order_updated', audit_log_handler)
EventManager.register_handler('work_order_completed', audit_log_handler)
EventManager.register_handler('equipment_status_changed', audit_log_handler)
EventManager.register_handler('checklist_completed', audit_log_handler)

# Register WebSocket handlers
EventManager.register_handler('work_order_created', websocket_notification_handler)
EventManager.register_handler('work_order_updated', websocket_notification_handler)
EventManager.register_handler('work_order_completed', websocket_notification_handler)
EventManager.register_handler('equipment_status_changed', websocket_notification_handler)
EventManager.register_handler('checklist_completed', websocket_notification_handler)


# Django signal receivers
@receiver(post_save, sender=OrdenesTrabajo)
def work_order_saved(sender, instance, created, **kwargs):
    """
    Handle work order save events
    """
    if created:
        EventManager.emit_event('work_order_created', {
            'work_order_id': instance.idordentrabajo,
            'work_order_number': instance.numeroot,
            'equipment_id': instance.idequipo.idequipo,
            'equipment_name': instance.idequipo.nombreequipo,
            'status': instance.idestadoot.nombreestadoot,
            'priority': instance.prioridad,
            'assigned_technician': instance.idtecnicoasignado.username if instance.idtecnicoasignado else None,
        })
    else:
        EventManager.emit_event('work_order_updated', {
            'work_order_id': instance.idordentrabajo,
            'work_order_number': instance.numeroot,
            'equipment_id': instance.idequipo.idequipo,
            'equipment_name': instance.idequipo.nombreequipo,
            'status': instance.idestadoot.nombreestadoot,
            'priority': instance.prioridad,
            'assigned_technician': instance.idtecnicoasignado.username if instance.idtecnicoasignado else None,
        })
        
        # Check if work order was completed
        if instance.idestadoot.nombreestadoot == 'Completada':
            EventManager.emit_event('work_order_completed', {
                'work_order_id': instance.idordentrabajo,
                'work_order_number': instance.numeroot,
                'equipment_id': instance.idequipo.idequipo,
                'equipment_name': instance.idequipo.nombreequipo,
                'completion_time': instance.fechacompletado.isoformat() if instance.fechacompletado else None,
            })


@receiver(post_save, sender=Equipos)
def equipment_saved(sender, instance, created, **kwargs):
    """
    Handle equipment save events
    """
    if not created:  # Only for updates
        EventManager.emit_event('equipment_status_changed', {
            'equipment_id': instance.idequipo,
            'equipment_name': instance.nombreequipo,
            'equipment_code': instance.codigointerno,
            'new_status': instance.idestadoactual.nombreestado,
            'location': instance.idfaenaactual.nombrefaena if instance.idfaenaactual else None,
        })


@receiver(post_save, sender=ChecklistInstance)
def checklist_completed_signal(sender, instance, created, **kwargs):
    """
    Handle checklist completion events
    """
    if created:
        EventManager.emit_event('checklist_completed', {
            'checklist_id': instance.id_instance,
            'equipment_id': instance.equipo.idequipo,
            'equipment_name': instance.equipo.nombreequipo,
            'operator': instance.operador.username,
            'inspection_date': instance.fecha_inspeccion.isoformat(),
            'template_name': instance.template.nombre,
        })
