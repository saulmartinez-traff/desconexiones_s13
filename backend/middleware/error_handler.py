"""
Error Handler Middleware - Manejo centralizado de errores
"""

import logging
import traceback
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """
    Middleware para manejo centralizado de errores HTTP.
    Captura excepciones no manejadas y retorna respuestas JSON consistentes.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            logger.error(
                f"Error no manejado: {str(e)}\n{traceback.format_exc()}",
                exc_info=True
            )
            
            # Retornar error JSON
            status_code = 500
            message = 'Error interno del servidor'
            
            if settings.DEBUG:
                message = str(e)
                details = traceback.format_exc()
            else:
                details = None
            
            return JsonResponse({
                'error': {
                    'status': status_code,
                    'message': message,
                    'details': details
                }
            }, status=status_code)
        
        return response
