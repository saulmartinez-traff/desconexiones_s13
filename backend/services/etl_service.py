"""
ETL Service - Extracción, Transformación y Carga de telemetría
Responsable de consumir datos de telemetría y procesarlos según reglas de negocio.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import requests
from django.conf import settings
from django.db import transaction

from apps.vehicles.models import Vehicle, Geofence
from apps.registers.models import Register
from apps.organization.models import Distribuidor

logger = logging.getLogger(__name__)


class ETLService:
    """
    Servicio de Extracción, Transformación y Carga (ETL).
    
    Responsabilidades:
    - Consumir endpoint de telemetría con paginación
    - Aplicar filtros (VIN contiene "SZ")
    - Validar datos
    - Procesar en lotes
    - Persistir en BD
    """
    
    def __init__(self):
        """Inicializar el servicio con configuración"""
        self.api_url = settings.TELEMETRY_API_URL
        self.api_key = settings.TELEMETRY_API_KEY
        self.vin_filter = settings.VIN_FILTER_PATTERN
        self.batch_size = settings.ETL_BATCH_SIZE
        self.page_size = settings.ETL_PAGE_SIZE
        self.timeout = settings.ETL_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
    
    def consume_telemetry_endpoint(self, max_pages: Optional[int] = None) -> List[Dict]:
        """
        Consume datos de telemetría desde API externa con paginación.
        
        Args:
            max_pages: Número máximo de páginas a consumir (None = todas)
        
        Returns:
            List[Dict]: Lista de registros de telemetría
        
        Raises:
            ConnectionError: Si hay error al conectar con el API
        """
        logger.info(f"Iniciando consumo de telemetría desde {self.api_url}")
        
        all_records = []
        page = 1
        
        try:
            while True:
                if max_pages and page > max_pages:
                    logger.info(f"Límite de páginas ({max_pages}) alcanzado")
                    break
                
                records = self._fetch_page(page)
                
                if not records:
                    logger.info(f"No hay más datos en página {page}")
                    break
                
                all_records.extend(records)
                logger.info(f"Página {page}: {len(records)} registros obtenidos")
                
                page += 1
        
        except Exception as e:
            logger.error(f"Error al consumir telemetría: {str(e)}", exc_info=True)
            raise ConnectionError(f"Fallo al conectar con API de telemetría: {str(e)}")
        
        logger.info(f"Total de registros obtenidos: {len(all_records)}")
        return all_records
    
    def _fetch_page(self, page: int) -> List[Dict]:
        """
        Obtiene una página específica del API.
        
        Args:
            page: Número de página
        
        Returns:
            List[Dict]: Registros de la página
        """
        try:
            response = self.session.get(
                self.api_url,
                params={
                    'page': page,
                    'page_size': self.page_size
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Asumir estructura: {results: [...], next: null}
            return data.get('results', [])
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener página {page}: {str(e)}")
            raise
    
    def apply_vin_filter(self, vehicles: List[Dict]) -> List[Dict]:
        """
        Filtro global: Solo procesar VINs que contengan patrón especificado.
        
        Args:
            vehicles: Lista de vehículos a filtrar
        
        Returns:
            List[Dict]: Vehículos que cumplen el filtro
        """
        logger.info(f"Aplicando filtro VIN (contiene '{self.vin_filter}') a {len(vehicles)} vehículos")
        
        filtered = [
            v for v in vehicles 
            if self.vin_filter in v.get('vin', '').upper()
        ]
        
        logger.info(f"Vehículos después del filtro VIN: {len(filtered)}")
        return filtered
    
    def validate_data(self, vehicles: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Valida datos de telemetría.
        
        Args:
            vehicles: Lista de vehículos a validar
        
        Returns:
            Tuple[valid, invalid]: Vehículos válidos e inválidos
        """
        logger.info(f"Validando {len(vehicles)} registros de telemetría")
        
        valid = []
        invalid = []
        
        for vehicle in vehicles:
            errors = self._validate_vehicle_record(vehicle)
            
            if errors:
                invalid.append({
                    'data': vehicle,
                    'errors': errors
                })
            else:
                valid.append(vehicle)
        
        logger.info(f"Validación completada: {len(valid)} válidos, {len(invalid)} inválidos")
        return valid, invalid
    
    def _validate_vehicle_record(self, vehicle: Dict) -> List[str]:
        """
        Valida un registro individual de vehículo.
        
        Args:
            vehicle: Datos del vehículo
        
        Returns:
            List[str]: Lista de errores encontrados
        """
        errors = []
        
        # Campos requeridos
        required_fields = ['vehicle_id', 'vin']
        for field in required_fields:
            if not vehicle.get(field):
                errors.append(f"Campo requerido faltante: {field}")
        
        # Validar VIN (17 caracteres)
        if vehicle.get('vin') and len(str(vehicle.get('vin'))) != 17:
            errors.append("VIN debe tener 17 caracteres")
        
        # Validar coordenadas si existen
        if vehicle.get('latitude'):
            try:
                lat = float(vehicle.get('latitude'))
                if not -90 <= lat <= 90:
                    errors.append("Latitud fuera de rango")
            except (ValueError, TypeError):
                errors.append("Latitud inválida")
        
        if vehicle.get('longitude'):
            try:
                lon = float(vehicle.get('longitude'))
                if not -180 <= lon <= 180:
                    errors.append("Longitud fuera de rango")
            except (ValueError, TypeError):
                errors.append("Longitud inválida")
        
        return errors
    
    @transaction.atomic
    def batch_process(self, vehicles: List[Dict], 
                     geofence_service: 'GeofenceService',
                     business_rules: 'DisconnectionRules') -> Dict:
        """
        Procesa vehículos en lotes (batch processing).
        
        Args:
            vehicles: Lista de vehículos a procesar
            geofence_service: Instancia del servicio de geocercas
            business_rules: Instancia de reglas de negocio
        
        Returns:
            Dict: Estadísticas del procesamiento
        """
        logger.info(f"Iniciando procesamiento en lotes de {len(vehicles)} vehículos")
        
        stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'errors': 0,
            'route_disconnections': 0,
            'base_disconnections': 0
        }
        
        # Procesar en lotes
        for i in range(0, len(vehicles), self.batch_size):
            batch = vehicles[i:i + self.batch_size]
            
            try:
                batch_stats = self._process_batch(
                    batch, 
                    geofence_service, 
                    business_rules
                )
                
                # Acumular estadísticas
                for key in batch_stats:
                    if key in stats and isinstance(stats[key], int):
                        stats[key] += batch_stats[key]
            
            except Exception as e:
                logger.error(f"Error procesando lote: {str(e)}", exc_info=True)
                stats['errors'] += len(batch)
        
        logger.info(f"Procesamiento completado. Stats: {stats}")
        return stats
    
    def _process_batch(self, vehicles: List[Dict],
                      geofence_service: 'GeofenceService',
                      business_rules: 'DisconnectionRules') -> Dict:
        """
        Procesa un lote individual de vehículos.
        
        Args:
            vehicles: Lote de vehículos
            geofence_service: Servicio de geocercas
            business_rules: Reglas de negocio
        
        Returns:
            Dict: Estadísticas del lote
        """
        stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'errors': 0,
            'route_disconnections': 0,
            'base_disconnections': 0
        }
        
        for vehicle_data in vehicles:
            try:
                vehicle_id = vehicle_data.get('vehicle_id')
                vin = vehicle_data.get('vin')
                
                # Obtener o crear vehículo
                vehicle, created = Vehicle.objects.get_or_create(
                    vehicle_id=vehicle_id,
                    defaults={
                        'vin': vin,
                        # ... otros campos
                    }
                )
                
                if created:
                    stats['created'] += 1
                    logger.info(f"Vehículo creado: {vin}")
                else:
                    stats['updated'] += 1
                
                # Actualizar ubicación
                if vehicle_data.get('latitude') and vehicle_data.get('longitude'):
                    vehicle.update_location(
                        vehicle_data['latitude'],
                        vehicle_data['longitude']
                    )
                
                # Determinar si está en geocerca
                in_geofence = geofence_service.is_in_geofence(
                    vehicle_data.get('latitude'),
                    vehicle_data.get('longitude'),
                    vehicle.geofence
                )
                
                # Clasificar desconexión
                disconnection_type = business_rules.classify_disconnection(
                    vehicle=vehicle,
                    speed=vehicle_data.get('speed', 0),
                    in_geofence=in_geofence,
                    geofence_name=vehicle.geofence.geo_name if vehicle.geofence else ''
                )
                
                # Crear registro de desconexión
                if business_rules.is_disconnection(vehicle_data):
                    register = Register.objects.create(
                        vehicle=vehicle,
                        distribuidor=vehicle.distribuidor,
                        last_connection=datetime.now(),
                        speed=vehicle_data.get('speed', 0),
                        geofence_name=vehicle.geofence.geo_name if vehicle.geofence else '',
                        disconnection_type=disconnection_type,
                        platform_client=vehicle_data.get('client', '')
                    )
                    
                    if disconnection_type == Register.DisconnectionType.DISCONNECTION_IN_ROUTE:
                        stats['route_disconnections'] += 1
                    else:
                        stats['base_disconnections'] += 1
                
                stats['processed'] += 1
            
            except Exception as e:
                logger.error(f"Error procesando vehículo {vehicle_data.get('vehicle_id')}: {str(e)}")
                stats['errors'] += 1
        
        return stats
    
    def close(self):
        """Cerrar conexión con API"""
        self.session.close()
        logger.info("Conexión con API cerrada")
