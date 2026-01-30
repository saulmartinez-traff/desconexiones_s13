# backend/apps/registers/models.py

"""
Registers Models - Gestión de registros de desconexiones y bitácora
Tablas: Register, Bitacora
"""

from django.db import models
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# REGISTER MODEL
# ============================================================================
class Register(models.Model):
    """
    Modelo de Registro - Evento de desconexión de vehículo.
    Relación N:1 con Vehicle.
    Relación 1:N con Bitacora.
    """
    
    # Identificador y relación
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.CASCADE,
        related_name='registers',
        help_text='Vehículo asociado al registro'
    )
    
    # Fecha de análisis/reporte
    report_date = models.DateField(
        auto_now_add=True,
        help_text='Fecha cuando se registró la desconexión',
        db_index=True
    )
    
    # Información del evento
    platform_client = models.CharField(
        max_length=100,
        blank=True,
        help_text='Cliente/plataforma que reportó el evento'
    )
    distribuidor = models.ForeignKey(
        'organization.Distribuidor',
        on_delete=models.PROTECT,
        related_name='registers',
        help_text='Distribuidor asociado en el momento del evento'
    )
    
    # Datos de la desconexión
    last_connection = models.DateTimeField(
        help_text='Última conexión registrada del vehículo'
    )
    problem = models.CharField(
        max_length=255,
        blank=True,
        help_text='Descripción del problema'
    )
    type = models.CharField(
        max_length=50,
        blank=True,
        help_text='Tipo de desconexión'
    )
    last_status = models.CharField(
        max_length=50,
        blank=True,
        help_text='Último estado conocido'
    )
    comentario = models.TextField(
        blank=True,
        help_text='Comentarios adicionales'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Registro de Desconexión'
        verbose_name_plural = 'Registros de Desconexión'
        ordering = ['-report_date', '-created_at']
        indexes = [
            models.Index(fields=['vehicle', 'report_date']),
            models.Index(fields=['report_date']),
            models.Index(fields=['last_status']),
        ]
    
    def __str__(self):
        return f"Registro {self.vehicle.vin[:8]}... ({self.report_date})"


# ============================================================================
# BITACORA MODEL
# ============================================================================
class Bitacora(models.Model):
    """
    Modelo de Bitácora - Registro de auditoría para cambios en registers.
    Relación N:1 con Register.
    Relación N:1 con User.
    Simple model: register, user, comentario
    """
    
    # Relación con Register
    register = models.ForeignKey(
        Register,
        on_delete=models.CASCADE,
        related_name='bitacora_entries',
        help_text='Registro asociado'
    )
    
    # Usuario que realizó la acción
    user = models.ForeignKey(
        'organization.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bitacora_entries',
        help_text='Usuario que realizó la acción'
    )
    
    # Comentario
    comentario = models.TextField(
        blank=True,
        help_text='Comentario sobre la acción'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Bitácora'
        verbose_name_plural = 'Bitácoras'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['register', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"Bitácora {self.register.id} por {self.user} ({self.created_at})"
    
    @staticmethod
    def log_action(register: Register, user: 'organization.User' = None, 
                   comentario: str = ''):
        """
        Crear una entrada en la bitácora.
        
        Args:
            register: Registro asociado
            user: Usuario que realizó la acción (opcional)
            comentario: Comentario adicional
        """
        bitacora = Bitacora.objects.create(
            register=register,
            user=user,
            comentario=comentario
        )
        logger.info(f"Bitácora creada: {bitacora}")
        return bitacora
