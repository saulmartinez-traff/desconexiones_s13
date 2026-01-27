"""
Business Rules Service - Reglas de negocio para clasificación de desconexiones
Implementa la lógica de determinación de tipo de desconexión.
"""

import logging
from typing import Optional

from apps.registers.models import Register

logger = logging.getLogger(__name__)


class DisconnectionRules:
    """
    Servicio de Reglas de Negocio.
    
    Responsabilidades:
    - Clasificar desconexiones según reglas
    - Validar velocidades
    - Determinar status final
    """
    
    # Velocidad mínima para considerar "en movimiento"
    MIN_SPEED_THRESHOLD = 5.0  # km/h
    
    def classify_disconnection(self, vehicle, speed: float = 0, 
                              in_geofence: bool = False,
                              geofence_name: str = '') -> str:
        """
        Clasifica el tipo de desconexión según reglas de negocio.
        
        Regla Principal:
        - Si speed > 0 Y geofence_name == "Fuera" → "Desconexión en trayecto"
        - Sino → "Desconexión en base"
        
        Args:
            vehicle: Instancia de Vehicle
            speed: Velocidad del vehículo en km/h
            in_geofence: ¿Está dentro de geocerca?
            geofence_name: Nombre de la geocerca
        
        Returns:
            str: Tipo de desconexión (ROUTE o BASE)
        """
        try:
            # Regla: Si velocidad > umbral Y está fuera de geocerca → trayecto
            if speed > self.MIN_SPEED_THRESHOLD and not in_geofence:
                logger.info(
                    f"Vehículo {vehicle.vin[:8]}... clasificado como "
                    f"DESCONEXIÓN EN TRAYECTO (speed={speed})"
                )
                return Register.DisconnectionType.DISCONNECTION_IN_ROUTE
            
            # Si no cumple → está en base
            logger.info(
                f"Vehículo {vehicle.vin[:8]}... clasificado como "
                f"DESCONEXIÓN EN BASE ({geofence_name})"
            )
            return Register.DisconnectionType.DISCONNECTION_AT_BASE
        
        except Exception as e:
            logger.error(f"Error clasificando desconexión: {str(e)}")
            return Register.DisconnectionType.UNKNOWN
    
    def is_disconnection(self, vehicle_data: dict) -> bool:
        """
        Determina si un evento representa una desconexión.
        
        Args:
            vehicle_data: Datos del vehículo/evento
        
        Returns:
            bool: True si es un evento de desconexión
        """
        # Aquí iría la lógica para determinar si es una desconexión
        # Por ahora, retorna True si falta conexión reciente
        return vehicle_data.get('is_disconnected', False)
    
    def validate_speed(self, speed: float) -> bool:
        """
        Valida que la velocidad sea válida.
        
        Args:
            speed: Velocidad en km/h
        
        Returns:
            bool: True si es válida
        """
        if speed is None:
            return False
        
        try:
            speed_float = float(speed)
            # Rango realista: 0-300 km/h
            return 0 <= speed_float <= 300
        except (ValueError, TypeError):
            return False
    
    def determine_status(self, problem: str) -> str:
        """
        Determina el estado final recomendado según el tipo de problema.
        
        Args:
            problem: Tipo de problema (ProblemType)
        
        Returns:
            str: Estado final recomendado
        """
        status_mapping = {
            Register.ProblemType.HARDWARE_FAILURE: Register.FinalStatus.WORKSHOP,
            Register.ProblemType.CONNECTION_LOSS: Register.FinalStatus.BASE,
            Register.ProblemType.LOW_BATTERY: Register.FinalStatus.BASE,
            Register.ProblemType.MALFUNCTION: Register.FinalStatus.WORKSHOP,
        }
        
        return status_mapping.get(problem, Register.FinalStatus.PENDING)
    
    def validate_responsible_assignment(self, responsible_user) -> bool:
        """
        Valida que el usuario asignado tenga permisos para resolver.
        
        Args:
            responsible_user: Instancia de User
        
        Returns:
            bool: True si puede ser asignado
        """
        if not responsible_user:
            return False
        
        # Solo Manager y Admin pueden ser asignados
        return responsible_user.is_manager()
    
    def get_priority_level(self, disconnection_type: str, 
                          problem: str) -> int:
        """
        Calcula nivel de prioridad (1=baja, 5=crítica).
        
        Args:
            disconnection_type: Tipo de desconexión
            problem: Tipo de problema
        
        Returns:
            int: Nivel de prioridad
        """
        priority = 1
        
        # Desconexión en trayecto es más crítica
        if disconnection_type == Register.DisconnectionType.DISCONNECTION_IN_ROUTE:
            priority += 2
        
        # Hardware failure es más crítica
        if problem == Register.ProblemType.HARDWARE_FAILURE:
            priority += 1
        
        return min(priority, 5)
