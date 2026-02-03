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
    
    # Choices para campos editables
    TIPO_MAL_FUNCIONAMIENTO = 'MAL FUNCIONAMIENTO'
    TIPO_OPERACION = 'OPERACIÓN'
    TIPO_CHOICES = [
        (TIPO_MAL_FUNCIONAMIENTO, 'Mal Funcionamiento'),
        (TIPO_OPERACION, 'Operación'),
    ]
    
    ESTATUS_POSIBLE_MANIPULACION = 'POSIBLE MANIPULACIÓN'
    ESTATUS_PERDIDA_SEÑAL = 'PERDIDA DE SEÑAL'
    ESTATUS_TALLER = 'TALLER'
    ESTATUS_CORTACORRIENTE = 'CORTACORRIENTE'
    ESTATUS_BASE = 'BASE'
    ESTATUS_ACCIDENTADA = 'ACCIDENTADA'
    ESTATUS_CHOICES = [
        (ESTATUS_POSIBLE_MANIPULACION, 'Posible Manipulación'),
        (ESTATUS_PERDIDA_SEÑAL, 'Perdida de Señal'),
        (ESTATUS_TALLER, 'Taller'),
        (ESTATUS_CORTACORRIENTE, 'Cortacorriente'),
        (ESTATUS_BASE, 'Base'),
        (ESTATUS_ACCIDENTADA, 'Accidentada'),
    ]
    
    RESPONSABLE_SIN_ESTATUS_DISTRIBUIDOR = 'SIN ESTATUS DEL DISTRIBUIDOR'
    RESPONSABLE_SIN_ESTATUS_CLIENTE = 'SIN ESTATUS DEL CLIENTE'
    RESPONSABLE_NO_OPERACIONAL = 'NO OPERACIONAL'
    RESPONSABLE_REVISION_FISICA = 'REVISIÓN FÍSICA'
    RESPONSABLE_CHOICES = [
        (RESPONSABLE_SIN_ESTATUS_DISTRIBUIDOR, 'Sin Estatus del Distribuidor'),
        (RESPONSABLE_SIN_ESTATUS_CLIENTE, 'Sin Estatus del Cliente'),
        (RESPONSABLE_NO_OPERACIONAL, 'No Operacional'),
        (RESPONSABLE_REVISION_FISICA, 'Revisión Física'),
    ]
    
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
    
    # Campos editables por usuario
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        default=TIPO_MAL_FUNCIONAMIENTO,
        help_text='Tipo de desconexión (editable por usuario)'
    )
    estatus_final = models.CharField(
        max_length=50,
        choices=ESTATUS_CHOICES,
        blank=True,
        help_text='Estatus final del registro (editable por usuario)'
    )
    responsable = models.CharField(
        max_length=50,
        choices=RESPONSABLE_CHOICES,
        default=RESPONSABLE_SIN_ESTATUS_DISTRIBUIDOR,
        help_text='Responsable del seguimiento (editable por usuario)'
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
