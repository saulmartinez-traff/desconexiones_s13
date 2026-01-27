"""
Services for Registers App
Business logic for register management and disconnection detection
"""

from typing import List, Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import Register, Bitacora
from apps.vehicles.models import Vehicle
from apps.organization.models import Distribuidor

logger = logging.getLogger(__name__)


class RegisterService:
    """
    Service for managing disconnection registers and audit trail
    """
    
    @staticmethod
    def create_register(
        vehicle: Vehicle,
        report_date,
        platform_client: str,
        distribuidor: Distribuidor,
        last_connection: datetime,
        problem: str = '',
        type_: str = '',
        last_status: str = '',
        comentario: str = ''
    ) -> Register:
        """
        Create a new disconnection register.
        
        Args:
            vehicle: Vehicle instance
            report_date: Date of the report
            platform_client: Client/platform that reported
            distribuidor: Distribuidor instance
            last_connection: Last connection datetime
            problem: Problem description
            type_: Disconnection type
            last_status: Last known status
            comentario: Additional comments
            
        Returns:
            Created Register instance
        """
        register = Register.objects.create(
            vehicle=vehicle,
            report_date=report_date,
            platform_client=platform_client,
            distribuidor=distribuidor,
            last_connection=last_connection,
            problem=problem,
            type=type_,
            last_status=last_status,
            comentario=comentario
        )
        
        # Log creation to bitacora
        Bitacora.log_action(
            register=register,
            comentario=f'Registro creado: {problem}'
        )
        
        logger.info(f"Register created: {register}")
        return register
    
    @staticmethod
    def update_register(
        register: Register,
        **kwargs
    ) -> Register:
        """
        Update a register with audit trail.
        
        Args:
            register: Register instance to update
            **kwargs: Fields to update (problem, type, last_status, comentario)
            
        Returns:
            Updated Register instance
        """
        changes = {}
        
        for field, value in kwargs.items():
            if field in ['problem', 'type', 'last_status', 'comentario']:
                old_value = getattr(register, field, None)
                if old_value != value:
                    changes[field] = (old_value, value)
                    setattr(register, field, value)
        
        if changes:
            register.save()
            
            # Log changes to bitacora
            change_summary = ', '.join([
                f'{field}: "{old}" → "{new}"' 
                for field, (old, new) in changes.items()
            ])
            Bitacora.log_action(
                register=register,
                comentario=f'Actualizado: {change_summary}'
            )
            
            logger.info(f"Register updated: {register}")
        
        return register
    
    @staticmethod
    def get_recent_disconnections(days: int = 7):
        """
        Get disconnection registers from the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            QuerySet of Register instances
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        return Register.objects.filter(
            report_date__gte=cutoff_date.date()
        ).select_related(
            'vehicle', 'distribuidor'
        ).order_by('-report_date', '-created_at')
    
    @staticmethod
    def get_vehicle_disconnections(vehicle: Vehicle):
        """
        Get all disconnection registers for a specific vehicle.
        
        Args:
            vehicle: Vehicle instance
            
        Returns:
            QuerySet of Register instances
        """
        return Register.objects.filter(
            vehicle=vehicle
        ).select_related('distribuidor').order_by('-report_date')
    
    @staticmethod
    def detect_disconnections(vehicles_data: List[Dict[str, Any]]) -> List[Register]:
        """
        Detect and register new disconnections from vehicle data.
        
        Args:
            vehicles_data: List of vehicle data from endpoint
            
        Returns:
            List of newly created Register instances
        """
        new_registers = []
        threshold_minutes = 5  # Consider disconnected if no contact for 5+ minutes
        
        for vehicle_data in vehicles_data:
            try:
                vehicle_id = vehicle_data.get('vehicle_id')
                vehicle = Vehicle.objects.get(vehicle_id=vehicle_id)
                
                # Check if vehicle is disconnected
                status = vehicle_data.get('status', 0)
                last_comm = vehicle_data.get('last_communication_time')
                
                if status == 0 or (last_comm and RegisterService._is_old_connection(last_comm, threshold_minutes)):
                    # Create register for disconnection
                    parsed_datetime = RegisterService._parse_datetime(last_comm)
                    register = RegisterService.create_register(
                        vehicle=vehicle,
                        report_date=timezone.now().date(),
                        platform_client=vehicle_data.get('client_name', ''),
                        distribuidor=vehicle.distribuidor,
                        last_connection=parsed_datetime or timezone.now(),
                        problem=f'Desconexión de vehículo - Status: {status}',
                        type_='DESCONEXION',
                        last_status=str(status),
                        comentario=f'Detected at {timezone.now().isoformat()}'
                    )
                    new_registers.append(register)
            
            except Vehicle.DoesNotExist:
                logger.warning(f"Vehicle {vehicle_data.get('vehicle_id')} not found")
                continue
            except Exception as e:
                logger.error(f"Error detecting disconnection for vehicle {vehicle_data.get('vehicle_id')}: {str(e)}")
                continue
        
        return new_registers
    
    @staticmethod
    def _is_old_connection(last_comm_str: Optional[str], threshold_minutes: int) -> bool:
        """
        Check if last communication is older than threshold.
        
        Args:
            last_comm_str: Last communication timestamp string
            threshold_minutes: Threshold in minutes
            
        Returns:
            True if connection is older than threshold
        """
        try:
            last_comm = RegisterService._parse_datetime(last_comm_str)
            if not last_comm:
                return True
            
            time_diff = timezone.now() - last_comm
            return time_diff > timedelta(minutes=threshold_minutes)
        except Exception:
            return True
    
    @staticmethod
    def _parse_datetime(datetime_str: Optional[str]) -> Optional[datetime]:
        """
        Parse datetime string from various formats.
        
        Args:
            datetime_str: Datetime string to parse
            
        Returns:
            datetime instance or None
        """
        if not datetime_str:
            return None
        
        try:
            # Try ISO format
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            return dt
        except (ValueError, AttributeError):
            try:
                # Try other common formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                    try:
                        dt = datetime.strptime(datetime_str, fmt)
                        return timezone.make_aware(dt)
                    except ValueError:
                        continue
            except Exception:
                pass
            
            return None
