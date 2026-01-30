# backend/apps/organization/models.py

"""
Organization Models - Estructura organizacional del sistema
Tablas: Distribuidores, Clients, Groups, Users
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# CUSTOM USER MODEL
# ============================================================================
class User(AbstractUser):
    """
    Extended User Model para incluir campos personalizados.
    Campos simplificados: user_name, user_pass, user_email
    """
    ADMIN = 'ADMIN'
    PM = 'PM'
    DIRECTOR = 'DIRECTOR'
    DISTRIBUIDOR = 'DISTRIBUIDOR'
    \
    ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (PM, 'Project Manager'),
        (DIRECTOR, 'Director cliente'),
        (DISTRIBUIDOR, 'Distribuidor'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=DISTRIBUIDOR,
    )
    
    distribuidor = models.ForeignKey(
        'Distribuidor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Distribuidor asociado al usuario'
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.username} ({self.email})"


# ============================================================================
# DISTRIBUIDOR MODEL
# ============================================================================
class Distribuidor(models.Model):
    """
    Modelo de Distribuidor - Empresa distribuidora de vehículos.
    Relación 1:N con Vehicles.
    Campos: distribuidor_id, distribuidor_name
    """
    
    distribuidor_id = models.IntegerField(
        unique=True,
        help_text='ID único del distribuidor en sistema externo'
    )
    distribuidor_name = models.CharField(
        max_length=255,
        help_text='Nombre del distribuidor'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Distribuidor'
        verbose_name_plural = 'Distribuidores'
        ordering = ['distribuidor_name']
        indexes = [
            models.Index(fields=['distribuidor_id']),
        ]
    
    def __str__(self):
        return f"{self.distribuidor_name} (ID: {self.distribuidor_id})"


# ============================================================================
# CLIENT MODEL
# ============================================================================
class Client(models.Model):
    """
    Modelo de Cliente - Entidad que consume vehículos (ej: BAJAS COPPEL).
    Relación 1:N con Groups.
    Campos: client_id, client_description
    """
    
    client_id = models.IntegerField(
        unique=True,
        help_text='ID único del cliente en sistema externo'
    )
    client_description = models.CharField(
        max_length=255,
        help_text='Descripción/nombre del cliente'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['client_description']
        indexes = [
            models.Index(fields=['client_id']),
        ]
    
    def __str__(self):
        return f"{self.client_description} (ID: {self.client_id})"


# ============================================================================
# GROUP MODEL
# ============================================================================
class Group(models.Model):
    """
    Modelo de Grupo - Agrupación de vehículos bajo un cliente.
    Relación N:1 con Client.
    Relación 1:N con Vehicles.
    Campos: group_id, group_description, client_id
    """
    
    group_id = models.IntegerField(
        unique=True,
        help_text='ID único del grupo en sistema externo'
    )
    group_description = models.CharField(
        max_length=255,
        help_text='Nombre/descripción del grupo (ej: "BAJAS COPPEL")'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='groups',
        help_text='Cliente propietario del grupo'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        ordering = ['group_description']
        indexes = [
            models.Index(fields=['group_id']),
            models.Index(fields=['client']),
        ]
    
    def __str__(self):
        return f"{self.group_description} (Cliente: {self.client.client_description})"
