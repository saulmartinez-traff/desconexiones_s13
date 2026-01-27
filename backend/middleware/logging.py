"""
Logging Middleware - Registro de requests/responses
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('api')


class LoggingMiddleware(MiddlewareMixin):
    """
    Middleware para logging de requests y responses.
    Registra método, ruta, status code y tiempo de procesamiento.
    """
    
    def process_request(self, request):
        """Registrar inicio de request"""
        request._start_time = time.time()
        logger.info(
            f"{request.method} {request.path} - "
            f"IP: {self._get_client_ip(request)}"
        )
    
    def process_response(self, request, response):
        """Registrar fin de request con duración"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            logger.info(
                f"{request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )
        
        return response
    
    @staticmethod
    def _get_client_ip(request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
