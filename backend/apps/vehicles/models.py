"""
Vehicles Models - Gestión de vehículos, geocercas y contratos
Tablas: Geofence, Vehicle, Contrato
"""

from django.db import models
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# GEOFENCE MODEL
# ============================================================================
class Geofence(models.Model):
    """
    Modelo de Geocerca - Simple storage del nombre de la geocerca.
    Relación 1:N con Vehicles.
    El procesamiento de geofencing se realiza en el endpoint externo.
    """
    
    geo_name = models.CharField(
        max_length=255,
        unique=True,
        help_text='Nombre de la geocerca (ej: "Base Centro")'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Geocerca'
        verbose_name_plural = 'Geocercas'
        ordering = ['geo_name']
        indexes = [
            models.Index(fields=['geo_name']),
        ]
    
    def __str__(self):
        return self.geo_name


# ============================================================================
# CONTRATO MODEL
# ============================================================================
class Contrato(models.Model):
    """
    Modelo de Contrato - Asocia VINs con contratos.
    Simple table que mapea VIN a contrato.
    """
    
    contrato_id = models.IntegerField(
        unique=True,
        help_text='ID único del contrato'
    )
    vin = models.CharField(
        max_length=17,
        help_text='Número de identificación del vehículo'
    )
    contrato = models.CharField(
        max_length=255,
        help_text='Número/referencia del contrato'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-contrato_id']
        indexes = [
            models.Index(fields=['contrato_id']),
            models.Index(fields=['vin']),
        ]
    
    def __str__(self):
        return f"Contrato {self.contrato} (VIN: {self.vin[:8]}...)"


# ============================================================================
# VEHICLE MODEL
# ============================================================================
class Vehicle(models.Model):
    """
    Modelo de Vehículo - Entidad principal del sistema.
    Relaciones:
    - N:1 con Group
    - N:1 con Distribuidor
    - N:1 con Geofence
    - N:1 con Contrato
    """
    
    # Identificadores
    vehicle_id = models.IntegerField(
        unique=True,
        help_text='ID único del vehículo en sistema externo'
    )
    vin = models.CharField(
        max_length=17,
        help_text='Número de identificación del vehículo',
        db_index=True
    )
    inner_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='ID interno del vehículo'
    )
    
    # Relaciones
    group = models.ForeignKey(
        'organization.Group',
        on_delete=models.PROTECT,
        related_name='vehicles',
        help_text='Grupo al que pertenece el vehículo'
    )
    distribuidor = models.ForeignKey(
        'organization.Distribuidor',
        on_delete=models.PROTECT,
        related_name='vehicles',
        help_text='Distribuidor responsable'
    )
    geofence = models.ForeignKey(
        Geofence,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicles',
        help_text='Geocerca/Base del vehículo'
    )
    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicles',
        help_text='Contrato asociado'
    )
    
    # Ubicación actual
    last_latitude = models.FloatField(
        null=True,
        blank=True,
        help_text='Última latitud registrada'
    )
    last_longitude = models.FloatField(
        null=True,
        blank=True,
        help_text='Última longitud registrada'
    )
    
    # Timestamp
    last_connection = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Última conexión/ping del vehículo',
        db_index=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        ordering = ['-last_connection']
        indexes = [
            models.Index(fields=['vehicle_id']),
            models.Index(fields=['vin']),
            models.Index(fields=['group']),
            models.Index(fields=['last_connection']),
        ]
    
    def __str__(self):
        return f"Vehículo {self.vin[:8]}... (ID: {self.vehicle_id})"
