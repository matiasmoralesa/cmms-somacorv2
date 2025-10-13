"""
Custom exceptions for CMMS API
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


class CMMSException(Exception):
    """Base exception for CMMS API"""
    def __init__(self, message, code=None, details=None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class EquipmentNotFoundError(CMMSException):
    """Raised when equipment is not found"""
    pass


class WorkOrderNotFoundError(CMMSException):
    """Raised when work order is not found"""
    pass


class InvalidWorkOrderStateError(CMMSException):
    """Raised when trying to perform invalid state transition"""
    pass


class InsufficientPermissionsError(CMMSException):
    """Raised when user lacks required permissions"""
    pass


class BotIntegrationError(CMMSException):
    """Raised when bot integration fails"""
    pass


def custom_exception_handler(exc, context):
    """
    Custom exception handler for CMMS API
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'message': 'An error occurred',
            'code': 'UNKNOWN_ERROR',
            'details': None,
            'timestamp': context.get('request').META.get('HTTP_X_TIMESTAMP', ''),
        }
        
        # Handle specific exceptions
        if isinstance(exc, CMMSException):
            custom_response_data.update({
                'message': exc.message,
                'code': exc.code or 'CMMS_ERROR',
                'details': exc.details,
            })
        elif isinstance(exc, ValidationError):
            custom_response_data.update({
                'message': 'Validation error',
                'code': 'VALIDATION_ERROR',
                'details': exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
            })
        elif isinstance(exc, IntegrityError):
            custom_response_data.update({
                'message': 'Database integrity error',
                'code': 'INTEGRITY_ERROR',
                'details': str(exc),
            })
        else:
            # Use default error message
            custom_response_data['message'] = response.data.get('detail', 'An error occurred')
            custom_response_data['code'] = 'API_ERROR'
        
        # Log the error
        logger.error(f"API Error: {custom_response_data['message']}", exc_info=True)
        
        response.data = custom_response_data
    
    return response
