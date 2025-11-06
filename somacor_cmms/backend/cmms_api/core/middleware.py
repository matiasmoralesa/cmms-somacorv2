"""
Custom middleware for CMMS API
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
import json

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all API requests and responses
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        
        # Log request
        if request.path.startswith('/api/'):
            # Log headers for debugging
            headers_info = {
                'Content-Type': request.META.get('CONTENT_TYPE', ''),
                'Authorization': 'Present' if 'HTTP_AUTHORIZATION' in request.META else 'None',
                'User-Agent': request.META.get('HTTP_USER_AGENT', '')[:100]
            }
            
            logger.info(
                f"🔵 API Request: {request.method} {request.path} - "
                f"User: {getattr(request.user, 'username', 'Anonymous')} - "
                f"IP: {self.get_client_ip(request)} - "
                f"Headers: {headers_info}"
            )
            
            # Log query parameters
            if request.GET:
                logger.info(f"📋 Query Params: {dict(request.GET)}")
            
            # Log POST data (without sensitive info)
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    body = request.body.decode('utf-8')
                    if body:
                        # Don't log passwords or tokens
                        import re
                        body_clean = re.sub(r'"(password|token|key)":\s*"[^"]*"', r'"\1": "[REDACTED]"', body)
                        logger.info(f"📤 Request Body: {body_clean[:500]}...")
                except:
                    logger.info(f"📤 Request Body: [Binary or invalid encoding]")
    
    def process_response(self, request, response):
        try:
            if hasattr(request, 'start_time') and request.path.startswith('/api/'):
                duration = time.time() - request.start_time
                
                # Log response with more details
                status_emoji = "✅" if response.status_code < 400 else "❌"
                
                # Get response size safely
                response_size = 0
                try:
                    if hasattr(response, 'content') and response.content:
                        response_size = len(response.content)
                except:
                    response_size = 0
                
                logger.info(
                    f"{status_emoji} API Response: {request.method} {request.path} - "
                    f"Status: {response.status_code} - "
                    f"Duration: {duration:.3f}s - "
                    f"Size: {response_size} bytes"
                )
                
                # Log response content for debugging (limited and safe)
                try:
                    if hasattr(response, 'content') and response.content:
                        content_preview = response.content.decode('utf-8')[:200]
                        logger.debug(f"📥 Response Content Preview: {content_preview}...")
                except Exception as e:
                    logger.debug(f"📥 Response Content: [Error decoding: {e}]")
        except Exception as e:
            logger.error(f"Error in process_response middleware: {e}")
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}
        super().__init__(get_response)
    
    def process_request(self, request):
        if not request.path.startswith('/api/'):
            return None
        
        # Get client IP
        ip = self.get_client_ip(request)
        current_time = time.time()
        
        # Clean old entries (older than 1 minute)
        self.requests = {
            k: v for k, v in self.requests.items() 
            if current_time - v['last_request'] < 60
        }
        
        # Check rate limit
        if ip in self.requests:
            if self.requests[ip]['count'] >= 100:  # 100 requests per minute
                return JsonResponse({
                    'success': False,
                    'error': {
                        'message': 'Rate limit exceeded',
                        'code': 'RATE_LIMIT_EXCEEDED',
                        'details': 'Too many requests. Please try again later.'
                    }
                }, status=429)
            self.requests[ip]['count'] += 1
        else:
            self.requests[ip] = {'count': 1, 'last_request': current_time}
        
        self.requests[ip]['last_request'] = current_time
        return None
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class BotIntegrationMiddleware(MiddlewareMixin):
    """
    Middleware to handle bot integration headers and authentication
    """
    
    def process_request(self, request):
        # Check if request is from bot
        bot_token = request.META.get('HTTP_X_BOT_TOKEN')
        if bot_token:
            # Validate bot token (implement your validation logic)
            if self.validate_bot_token(bot_token):
                request.is_bot_request = True
                request.bot_token = bot_token
            else:
                return JsonResponse({
                    'success': False,
                    'error': {
                        'message': 'Invalid bot token',
                        'code': 'INVALID_BOT_TOKEN',
                        'details': 'The provided bot token is invalid or expired.'
                    }
                }, status=401)
        else:
            request.is_bot_request = False
    
    def validate_bot_token(self, token):
        """
        Validate bot token - implement your validation logic
        """
        # For now, accept any token that starts with 'bot_'
        # In production, implement proper token validation
        return token.startswith('bot_')
