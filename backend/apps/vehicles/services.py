"""
Services for Vehicles App
ETL services for importing vehicle data from external endpoints
"""

from typing import List, Dict, Any
from django.db import transaction
from django.utils import timezone
from datetime import datetime
import logging

from .models import Vehicle, Geofence, Contrato
from apps.organization.models import Group, Distribuidor

logger = logging.getLogger(__name__)


class VehicleETLService:
    """
    Service for extracting, transforming, and loading vehicle data
    from external endpoint to database
    """
    
    @staticmethod
    def import_vehicle_data(endpoint_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Import vehicle data from endpoint into database.
        
        Expected endpoint structure:
        {
            "vehicle_id": int,
            "vin": str,
            "license_nmbr": str,
            "status": int,
            "last_communication_time": str,
            "latitude": float,
            "longitude": float,
            "speed": float,
            "client_id": int,
            "client_name": str,
            "group_id": int,
            "group_name": str,
            "geofence_name": str
        }
        
        Args:
            endpoint_data: List of vehicle data dictionaries from endpoint
            
        Returns:
            Dict with import statistics:
            {
                "created": int,
                "updated": int,
                "failed": int,
                "errors": List[str]
            }
        """
        stats = {
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }
        
        if not endpoint_data:
            logger.warning("No vehicle data provided for import")
            return stats
        
        with transaction.atomic():
            for vehicle_data in endpoint_data:
                try:
                    result = VehicleETLService._process_vehicle(vehicle_data)
                    if result["action"] == "created":
                        stats["created"] += 1
                    elif result["action"] == "updated":
                        stats["updated"] += 1
                except Exception as e:
                    stats["failed"] += 1
                    error_msg = f"Error processing vehicle {vehicle_data.get('vehicle_id')}: {str(e)}"
                    stats["errors"].append(error_msg)
                    logger.error(error_msg)
        
        logger.info(f"Vehicle import completed - Created: {stats['created']}, Updated: {stats['updated']}, Failed: {stats['failed']}")
        return stats
    
    @staticmethod
    def _process_vehicle(vehicle_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Process a single vehicle record from endpoint.
        
        Args:
            vehicle_data: Vehicle data dictionary from endpoint
            
        Returns:
            Dict with action taken: {"action": "created"|"updated", "vehicle_id": int}
        """
        vehicle_id = vehicle_data.get('vehicle_id')
        
        if not vehicle_id:
            raise ValueError("vehicle_id is required")
        
        # Get or create Group
        group_id = vehicle_data.get('group_id')
        group_name = vehicle_data.get('group_name', 'Unknown')
        
        if group_id:
            group, _ = Group.objects.get_or_create(
                group_id=group_id,
                defaults={'group_description': group_name, 'client_id': vehicle_data.get('client_id')}
            )
        else:
            raise ValueError(f"group_id is required for vehicle {vehicle_id}")
        
        # Get or create Distribuidor
        distribuidor_name = vehicle_data.get('client_name', 'Unknown')
        distribuidor, _ = Distribuidor.objects.get_or_create(
            distribuidor_id=vehicle_data.get('client_id', 0),
            defaults={'distribuidor_name': distribuidor_name}
        )
        
        # Get or create Geofence
        geofence = None
        geofence_name = vehicle_data.get('geofence_name')
        if geofence_name:
            geofence, _ = Geofence.objects.get_or_create(
                geo_name=geofence_name
            )
        
        # Get or create Contrato if VIN exists
        contrato = None
        vin = vehicle_data.get('vin', '')
        if vin:
            try:
                contrato = Contrato.objects.get(vin=vin)
            except Contrato.DoesNotExist:
                # Contrato might not exist yet, which is OK
                pass
        
        # Parse last_communication_time
        last_connection = None
        last_comm = vehicle_data.get('last_communication_time')
        if last_comm:
            try:
                # Try parsing ISO format
                last_connection = datetime.fromisoformat(last_comm.replace('Z', '+00:00'))
                if timezone.is_naive(last_connection):
                    last_connection = timezone.make_aware(last_connection)
            except (ValueError, AttributeError):
                logger.warning(f"Could not parse last_communication_time: {last_comm}")
        
        # Create or update Vehicle
        vehicle, created = Vehicle.objects.update_or_create(
            vehicle_id=vehicle_id,
            defaults={
                'vin': vin,
                'group': group,
                'distribuidor': distribuidor,
                'geofence': geofence,
                'contrato': contrato,
                'last_latitude': vehicle_data.get('latitude'),
                'last_longitude': vehicle_data.get('longitude'),
                'last_connection': last_connection,
                'inner_id': vehicle_data.get('inner_id'),
            }
        )
        
        return {
            "action": "created" if created else "updated",
            "vehicle_id": vehicle_id
        }
    
    @staticmethod
    def sync_vehicles_with_endpoint(vehicles_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sync vehicles from endpoint with database, updating timestamps.
        
        Args:
            vehicles_data: List of vehicle data from endpoint
            
        Returns:
            Import statistics dictionary
        """
        return VehicleETLService.import_vehicle_data(vehicles_data)
