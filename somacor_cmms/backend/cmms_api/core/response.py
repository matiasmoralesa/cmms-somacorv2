"""
Standardized response utilities for CMMS API
"""
from rest_framework.response import Response
from rest_framework import status
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class APIResponse:
    """
    Standardized API response utility class
    """
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK,
        meta: Optional[Dict] = None
    ) -> Response:
        """
        Create a standardized success response
        """
        response_data = {
            'success': True,
            'message': message,
            'data': data,
            'timestamp': None,  # Will be set by middleware
        }
        
        if meta:
            response_data['meta'] = meta
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        code: str = "UNKNOWN_ERROR",
        details: Any = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        meta: Optional[Dict] = None
    ) -> Response:
        """
        Create a standardized error response
        """
        response_data = {
            'success': False,
            'error': {
                'message': message,
                'code': code,
                'details': details,
            },
            'timestamp': None,  # Will be set by middleware
        }
        
        if meta:
            response_data['meta'] = meta
            
        # Log the error
        logger.error(f"API Error: {message} (Code: {code})")
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def paginated(
        data: Any,
        count: int,
        next_url: Optional[str] = None,
        previous_url: Optional[str] = None,
        message: str = "Success"
    ) -> Response:
        """
        Create a standardized paginated response
        """
        response_data = {
            'success': True,
            'message': message,
            'data': data,
            'pagination': {
                'count': count,
                'next': next_url,
                'previous': previous_url,
            },
            'timestamp': None,  # Will be set by middleware
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "Resource created successfully",
        location: Optional[str] = None
    ) -> Response:
        """
        Create a standardized created response
        """
        response_data = {
            'success': True,
            'message': message,
            'data': data,
            'timestamp': None,  # Will be set by middleware
        }
        
        headers = {}
        if location:
            headers['Location'] = location
            
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
    @staticmethod
    def no_content(message: str = "Resource deleted successfully") -> Response:
        """
        Create a standardized no content response
        """
        response_data = {
            'success': True,
            'message': message,
            'timestamp': None,  # Will be set by middleware
        }
        
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)
