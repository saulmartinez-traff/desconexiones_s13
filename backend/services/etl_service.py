"""
ETL Service - Extracción, Transformación y Carga de telemetría
Responsable de consumir datos de telemetría y procesarlos según reglas de negocio.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import os
import dotenv
import requests
import pandas as pd
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from apps.vehicles.models import Vehicle, Geofence
from apps.registers.models import Register
from apps.organization.models import Client, Group, Distribuidor

dotenv.load_dotenv()
logger = logging.getLogger(__name__)


class ETLService:
    """
    Servicio de Extracción, Transformación y Carga (ETL).
    
    Responsabilidades:
    - Consumir endpoint de telemetría con paginación
    - Procesar estructura: {data: [], total, page, page_size, total_pages}
    - Crear/actualizar: Client, Group, Geofence, Vehicle, Register
    - Aplicar lógica de desconexión
    - Configurar valores por defecto
    """
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Inicializar el servicio con configuración.
        
        Args:
            api_url: URL de la API (opcional, usa settings si no se proporciona)
        """
        self.api_url = os.getenv('TELEMETRY_API_URL')
        self.page_size = 1000  # Tamaño óptimo según especificación
        self.max_page_size = 5000  # Máximo permitido
        self.timeout = getattr(settings, 'ETL_TIMEOUT', 30)
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def run_etl(self, max_pages: Optional[int] = None) -> Dict:
        """
        Ejecuta el proceso ETL completo.
        
        Args:
            max_pages: Número máximo de páginas a procesar (None = todas)
        
        Returns:
            Dict: Estadísticas del procesamiento
        """
        logger.info("=== Iniciando proceso ETL ===")
        
        stats = {
            'total_records': 0,
            'clients_created': 0,
            'groups_created': 0,
            'geofences_created': 0,
            'vehicles_created': 0,
            'vehicles_updated': 0,
            'registers_created': 0,
            'disconnections_route': 0,
            'disconnections_base': 0,
            'errors': 0
        }
        
        try:
            # 1. Extraer datos de la API
            all_data = self._extract_data(max_pages)
            stats['total_records'] = len(all_data)
            
            # 2. Transformar y cargar datos
            process_stats = self._transform_and_load(all_data)
            stats.update(process_stats)
            
            logger.info(f"=== ETL completado exitosamente ===")
            logger.info(f"Estadísticas: {stats}")
            
        except Exception as e:
            logger.error(f"Error en proceso ETL: {str(e)}", exc_info=True)
            stats['errors'] += 1
            raise
        
        return stats
    
    def _extract_data(self, max_pages: Optional[int] = None) -> List[Dict]:
        """
        Extrae datos de la API con paginación.
        
        Args:
            max_pages: Número máximo de páginas a consumir
        
        Returns:
            List[Dict]: Lista de registros de telemetría
        """
        if not self.api_url:
            raise ValueError("API URL no configurada. Configura TELEMETRY_API_URL en settings.")
        
        logger.info(f"Extrayendo datos desde {self.api_url}")
        
        all_records = []
        page = 1
        
        while True:
            if max_pages and page > max_pages:
                logger.info(f"Límite de páginas ({max_pages}) alcanzado")
                break
            
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
                
                # Estructura esperada: {data: [], total, page, page_size, total_pages}
                records = data.get('data', [])
                
                if not records:
                    logger.info(f"No hay más datos en página {page}")
                    break
                
                all_records.extend(records)
                logger.info(f"Página {page}/{data.get('total_pages', '?')}: {len(records)} registros")
                
                # Verificar si hay más páginas
                if page >= data.get('total_pages', page):
                    logger.info("Última página alcanzada")
                    break
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error al obtener página {page}: {str(e)}")
                raise ConnectionError(f"Fallo al conectar con API: {str(e)}")
        
        df = pd.DataFrame(all_records)
        df = df[~df['group_id'].isin([30201,35761,47365,55617])]
        logger.info(f"Total de registros extraídos: {len(all_records)}")
        return df.to_dict('records')
    
    @transaction.atomic
    def _transform_and_load(self, records: List[Dict]) -> Dict:
        """
        Transforma y carga datos en la base de datos.
        
        Args:
            records: Lista de registros de telemetría
        
        Returns:
            Dict: Estadísticas del procesamiento
        """
        logger.info(f"Transformando y cargando {len(records)} registros")
        
        stats = {
            'clients_created': 0,
            'groups_created': 0,
            'geofences_created': 0,
            'vehicles_created': 0,
            'vehicles_updated': 0,
            'registers_created': 0,
            'disconnections_route': 0,
            'disconnections_base': 0,
            'errors': 0
        }
        
        for record in records:
            try:
                # 1. Crear/obtener Client
                client, client_created = self._get_or_create_client(record)
                if client_created:
                    stats['clients_created'] += 1
                
                # 2. Crear/obtener Group
                group, group_created = self._get_or_create_group(record, client)
                if group_created:
                    stats['groups_created'] += 1
                
                # 3. Crear/obtener Geofence
                geofence = None
                if record.get('geofence_name'):
                    geofence, geo_created = self._get_or_create_geofence(record)
                    if geo_created:
                        stats['geofences_created'] += 1
                
                # 4. Crear/obtener Distribuidor (por ahora sin datos)
                distribuidor = self._get_default_distribuidor()
                
                # 5. Crear/actualizar Vehicle
                vehicle, vehicle_created = self._get_or_create_vehicle(
                    record, group, distribuidor, geofence
                )
                if vehicle_created:
                    stats['vehicles_created'] += 1
                else:
                    stats['vehicles_updated'] += 1
                
                # 6. Verificar si hay desconexión y crear Register
                if self._is_disconnected(record):
                    register_stats = self._create_register(record, vehicle, distribuidor)
                    stats['registers_created'] += register_stats['created']
                    stats['disconnections_route'] += register_stats['route']
                    stats['disconnections_base'] += register_stats['base']
                
            except Exception as e:
                logger.error(f"Error procesando registro {record.get('vehicle_id')}: {str(e)}")
                stats['errors'] += 1
                continue
        
        return stats
    
    def _get_or_create_client(self, record: Dict) -> Tuple[Client, bool]:
        """Obtiene o crea un Client."""
        client_id = record.get('client_id')
        client_name = record.get('client_name', f'Cliente {client_id}')
        
        client, created = Client.objects.get_or_create(
            client_id=client_id,
            defaults={
                'client_description': client_name
            }
        )
        
        if created:
            logger.info(f"Cliente creado: {client_name} (ID: {client_id})")
        
        return client, created
    
    def _get_or_create_group(self, record: Dict, client: Client) -> Tuple[Group, bool]:
        """Obtiene o crea un Group."""
        group_id = record.get('group_id')
        group_name = record.get('group_name', f'Grupo {group_id}')
        
        group, created = Group.objects.get_or_create(
            group_id=group_id,
            defaults={
                'group_description': group_name,
                'client': client
            }
        )
        
        if created:
            logger.info(f"Grupo creado: {group_name} (ID: {group_id})")
        
        return group, created
    
    def _get_or_create_geofence(self, record: Dict) -> Tuple[Geofence, bool]:
        """Obtiene o crea una Geofence."""
        geo_name = record.get('geofence_name')
        
        if not geo_name:
            return None, False
        
        geofence, created = Geofence.objects.get_or_create(
            geo_name=geo_name
        )
        
        if created:
            logger.info(f"Geocerca creada: {geo_name}")
        
        return geofence, created
    
    def _get_default_distribuidor(self) -> Distribuidor:
        """
        Obtiene o crea un distribuidor por defecto.
        En el futuro esto se obtendrá del Excel o API.
        """
        distribuidor, created = Distribuidor.objects.get_or_create(
            distribuidor_id=0,
            defaults={
                'distribuidor_name': 'Sin Distribuidor'
            }
        )
        
        if created:
            logger.info("Distribuidor por defecto creado")
        
        return distribuidor
    
    def _get_or_create_vehicle(
        self, 
        record: Dict, 
        group: Group, 
        distribuidor: Distribuidor,
        geofence: Optional[Geofence]
    ) -> Tuple[Vehicle, bool]:
        """Obtiene o crea un Vehicle."""
        vehicle_id = record.get('vehicle_id')
        vin = record.get('vin')
        
        # Parsear last_communication_time
        last_connection = self._parse_datetime(record.get('last_communication_time'))
        
        vehicle, created = Vehicle.objects.update_or_create(
            vehicle_id=vehicle_id,
            defaults={
                'vin': vin,
                'group': group,
                'distribuidor': distribuidor,
                'geofence': geofence,
                'last_latitude': record.get('latitude'),
                'last_longitude': record.get('longitude'),
                'last_connection': last_connection,
                'speed': record.get('speed', 0.0),
            }
        )
        
        if created:
            logger.debug(f"Vehículo creado: {vin} (ID: {vehicle_id})")
        else:
            logger.debug(f"Vehículo actualizado: {vin} (ID: {vehicle_id})")
        
        return vehicle, created
    
    def _is_disconnected(self, record: Dict) -> bool:
        """
        Determina si un vehículo está desconectado.
        
        Regla: last_communication_time < día actual
        """
        last_comm = self._parse_datetime(record.get('last_communication_time'))
        
        if not last_comm:
            return False
        
        # Comparar fecha (sin hora)
        today = timezone.now().date()
        last_comm_date = last_comm.date()
        
        is_disconnected = last_comm_date < today
        
        return is_disconnected
    
    def _create_register(
        self, 
        record: Dict, 
        vehicle: Vehicle, 
        distribuidor: Distribuidor
    ) -> Dict:
        """
        Crea un registro de desconexión.
        
        Lógica de problema:
        - Si speed > 0 AND geofence_name == null → "Desconexión en trayecto"
        - Caso contrario → "Desconexión en base"
        
        Valores por defecto:
        - tipo = "MAL FUNCIONAMIENTO"
        - estatus_final = "POSIBLE MANIPULACIÓN" (base) o "PERDIDA DE SEÑAL" (trayecto)
        - responsable = "SIN ESTATUS DEL DISTRIBUIDOR"
        """
        stats = {'created': 0, 'route': 0, 'base': 0}
        
        # Determinar tipo de desconexión
        speed = record.get('speed', 0)
        geofence_name = record.get('geofence_name')
        
        if speed > 0 and not geofence_name:
            problem = "Desconexión en trayecto"
            estatus_final = Register.ESTATUS_PERDIDA_SEÑAL
            stats['route'] = 1
        else:
            problem = "Desconexión en base"
            estatus_final = Register.ESTATUS_POSIBLE_MANIPULACION
            stats['base'] = 1
        
        # Verificar si ya existe un registro activo para este vehículo
        # Solo crear nuevo registro si no existe uno reciente
        today = timezone.now().date()
        existing = Register.objects.filter(
            vehicle=vehicle,
            report_date=today
        ).first()
        
        if existing:
            logger.debug(f"Registro ya existe para vehículo {vehicle.vin} hoy")
            return stats
        
        # Crear registro
        last_connection = self._parse_datetime(record.get('last_communication_time'))
        
        register = Register.objects.create(
            vehicle=vehicle,
            distribuidor=distribuidor,
            platform_client=record.get('client_name', ''),
            last_connection=last_connection,
            problem=problem,
            tipo=Register.TIPO_MAL_FUNCIONAMIENTO,
            estatus_final=estatus_final,
            responsable=Register.RESPONSABLE_SIN_ESTATUS_DISTRIBUIDOR,
            comentario=''
        )
        
        stats['created'] = 1
        logger.info(f"Registro creado: {vehicle.vin} - {problem}")
        
        return stats
    
    def _parse_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """
        Parsea string de fecha/hora a datetime.
        
        Args:
            dt_string: String de fecha/hora
        
        Returns:
            datetime o None si no se puede parsear
        """
        if not dt_string:
            return None
        
        try:
            # Intentar varios formatos comunes
            formats = [
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%d',
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(dt_string, fmt)
                    # Hacer timezone-aware
                    if timezone.is_naive(dt):
                        dt = timezone.make_aware(dt)
                    return dt
                except ValueError:
                    continue
            
            logger.warning(f"No se pudo parsear fecha: {dt_string}")
            return None
            
        except Exception as e:
            logger.error(f"Error parseando fecha {dt_string}: {str(e)}")
            return None
    
    def close(self):
        """Cerrar conexión con API."""
        self.session.close()
        logger.info("Conexión con API cerrada")
