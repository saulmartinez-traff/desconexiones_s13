"""
Geofence Service - Geoprocesamiento y validación de geocercas
Responsable de determinar si un vehículo está dentro/fuera de una geocerca.
"""

import logging
from typing import Optional, Tuple
from math import radians, sin, cos, sqrt, atan2

from apps.vehicles.models import Geofence

logger = logging.getLogger(__name__)


class GeofenceService:
    """
    Servicio de Geoprocesamiento.
    
    Responsabilidades:
    - Validar si un punto está dentro de una geocerca
    - Soportar polígonos (ray casting algorithm)
    - Soportar círculos (haversine distance)
    - Cache de geocercas frecuentes
    """
    
    # Constante: Radio de la Tierra en km
    EARTH_RADIUS_KM = 6371
    
    def __init__(self):
        """Inicializar el servicio con caché"""
        self._geofence_cache = {}
    
    def is_in_geofence(self, latitude: float, longitude: float, 
                      geofence: Optional[Geofence]) -> bool:
        """
        Verifica si un punto está dentro de una geocerca.
        
        Args:
            latitude: Latitud del punto
            longitude: Longitud del punto
            geofence: Instancia de Geofence (o None)
        
        Returns:
            bool: True si está dentro, False si está fuera o no hay geocerca
        """
        if not geofence or not all([latitude, longitude]):
            return False
        
        # Usar método del modelo
        return geofence.is_point_inside(latitude, longitude)
    
    def get_geofence_name(self, geofence: Optional[Geofence]) -> str:
        """
        Obtiene el nombre de la geocerca.
        
        Args:
            geofence: Instancia de Geofence
        
        Returns:
            str: Nombre de la geocerca o "Fuera"
        """
        if geofence:
            return geofence.geo_name
        return "Fuera"
    
    def find_geofence_by_location(self, latitude: float, 
                                  longitude: float) -> Optional[Geofence]:
        """
        Encuentra la geocerca que contiene las coordenadas dadas.
        Útil para asignar una geocerca a un vehículo basado en ubicación.
        
        Args:
            latitude: Latitud
            longitude: Longitud
        
        Returns:
            Geofence: Primera geocerca que contiene el punto, o None
        """
        try:
            for geofence in Geofence.objects.filter(is_active=True):
                if geofence.is_point_inside(latitude, longitude):
                    logger.info(f"Geocerca encontrada: {geofence.geo_name}")
                    return geofence
            
            logger.info(f"No se encontró geocerca para {latitude}, {longitude}")
            return None
        
        except Exception as e:
            logger.error(f"Error buscando geocerca: {str(e)}")
            return None
    
    def validate_polygon(self, coordinates: list) -> Tuple[bool, str]:
        """
        Valida que un polígono sea válido.
        
        Args:
            coordinates: Lista de [lat, lon] pares
        
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        if not coordinates or len(coordinates) < 3:
            return False, "Polígono debe tener al menos 3 puntos"
        
        for point in coordinates:
            if not isinstance(point, (list, tuple)) or len(point) != 2:
                return False, f"Punto inválido: {point}"
            
            lat, lon = point
            if not (-90 <= lat <= 90):
                return False, f"Latitud fuera de rango: {lat}"
            if not (-180 <= lon <= 180):
                return False, f"Longitud fuera de rango: {lon}"
        
        # Verificar si el primer y último punto cierran el polígono
        if coordinates[0] != coordinates[-1]:
            logger.warning("El polígono no está cerrado, se cierra automáticamente")
        
        return True, "Polígono válido"
    
    def validate_circle(self, circle_data: dict) -> Tuple[bool, str]:
        """
        Valida que un círculo sea válido.
        
        Args:
            circle_data: Dict con {lat, lon, radius_km}
        
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        try:
            lat = circle_data.get('lat')
            lon = circle_data.get('lon')
            radius_km = circle_data.get('radius_km')
            
            if not all([lat, lon, radius_km]):
                return False, "Círculo debe tener lat, lon y radius_km"
            
            if not (-90 <= lat <= 90):
                return False, f"Latitud fuera de rango: {lat}"
            if not (-180 <= lon <= 180):
                return False, f"Longitud fuera de rango: {lon}"
            if radius_km <= 0:
                return False, f"Radio debe ser positivo: {radius_km}"
            
            return True, "Círculo válido"
        
        except Exception as e:
            return False, f"Error validando círculo: {str(e)}"
    
    def calculate_distance(self, lat1: float, lon1: float, 
                         lat2: float, lon2: float) -> float:
        """
        Calcula distancia entre dos puntos usando Haversine formula.
        
        Args:
            lat1, lon1: Punto 1
            lat2, lon2: Punto 2
        
        Returns:
            float: Distancia en km
        """
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return self.EARTH_RADIUS_KM * c
    
    def clear_cache(self):
        """Limpiar caché de geocercas"""
        self._geofence_cache.clear()
        logger.info("Caché de geocercas limpiado")
