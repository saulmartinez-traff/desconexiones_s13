"""
Analytics Service - Agregaciones y cálculos para reportes
Responsable de generar datos para la vista de Resumen (matriz dinámica).
"""

import logging
from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import Q, Count, Sum, Avg
from django.db.models.functions import TruncDate

from apps.vehicles.models import Vehicle
from apps.registers.models import Register
from apps.organization.models import Group, Contrato

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Servicio de Análisis y Agregaciones.
    
    Responsabilidades:
    - Generar matriz de datos (conectado/desconectado por fecha y grupo)
    - Calcular métricas de SLA
    - Generar reportes ejecutivos
    """
    
    def __init__(self):
        """Inicializar el servicio"""
        pass
    
    def get_summary_matrix(self, start_date: datetime = None, 
                          end_date: datetime = None,
                          group_id: int = None) -> Dict:
        """
        Genera matriz de resumen por fecha y grupo.
        
        Estructura retornada:
        {
            "dates": ["2025-01-20", "2025-01-21", ...],
            "groups": [
                {
                    "group_name": "BAJAS COPPEL",
                    "contract": "Inventario A",
                    "data": [
                        {"connected": 150, "disconnected": 5, "unknown": 2},
                        ...
                    ]
                }
            ]
        }
        
        Args:
            start_date: Fecha inicial (default: hace 30 días)
            end_date: Fecha final (default: hoy)
            group_id: ID del grupo a filtrar (opcional)
        
        Returns:
            Dict: Matriz de datos estructurada
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        logger.info(f"Generando matriz de resumen ({start_date.date()} a {end_date.date()})")
        
        # Obtener todas las fechas en el rango
        dates = self._get_date_range(start_date, end_date)
        
        # Obtener grupos (con opción de filtro)
        groups_query = Group.objects.filter(is_active=True)
        if group_id:
            groups_query = groups_query.filter(id=group_id)
        
        groups_data = []
        
        for group in groups_query:
            group_matrix = {
                'group_name': group.group_description,
                'group_id': group.group_id,
                'data': []
            }
            
            # Procesar datos por contrato/inventario
            for contract in group.vehicles.values('contrato').distinct():
                contract_id = contract['contrato']
                contract_obj = Contrato.objects.get(id=contract_id) if contract_id else None
                
                contract_data = {
                    'contract_name': contract_obj.contrato if contract_obj else 'N/A',
                    'contract_id': contract_id,
                    'daily_data': []
                }
                
                # Procesar cada fecha
                for date in dates:
                    daily_stats = self._get_daily_stats(
                        group_id=group.id,
                        contract_id=contract_id,
                        date=date
                    )
                    contract_data['daily_data'].append(daily_stats)
                
                group_matrix['data'].append(contract_data)
            
            groups_data.append(group_matrix)
        
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in dates],
            'groups': groups_data
        }
    
    def _get_date_range(self, start_date: datetime, 
                       end_date: datetime) -> List[datetime]:
        """
        Genera lista de fechas entre dos rangos.
        
        Args:
            start_date: Fecha inicial
            end_date: Fecha final
        
        Returns:
            List[datetime]: Lista de fechas
        """
        dates = []
        current_date = start_date.date()
        end = end_date.date()
        
        while current_date <= end:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        return dates
    
    def _get_daily_stats(self, group_id: int, 
                        contract_id: int, date) -> Dict:
        """
        Obtiene estadísticas para un grupo/contrato/fecha específica.
        
        Args:
            group_id: ID del grupo
            contract_id: ID del contrato
            date: Fecha a analizar
        
        Returns:
            Dict: Estadísticas del día
        """
        # Vehículos en el grupo/contrato
        vehicles = Vehicle.objects.filter(
            group_id=group_id,
            is_active=True
        )
        
        if contract_id:
            vehicles = vehicles.filter(contrato_id=contract_id)
        
        total_vehicles = vehicles.count()
        
        # Registros de desconexión en el día
        disconnection_records = Register.objects.filter(
            vehicle__in=vehicles,
            report_date=date
        )
        
        disconnected = disconnection_records.exclude(
            final_status=Register.FinalStatus.RESOLVED
        ).count()
        
        connected = total_vehicles - disconnected
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'total': total_vehicles,
            'connected': connected,
            'disconnected': disconnected,
            'percentage_connected': (connected / total_vehicles * 100) if total_vehicles > 0 else 0
        }
    
    def get_group_statistics(self, group_id: int, 
                            days: int = 30) -> Dict:
        """
        Obtiene estadísticas agregadas para un grupo.
        
        Args:
            group_id: ID del grupo
            days: Número de días a analizar
        
        Returns:
            Dict: Estadísticas del grupo
        """
        start_date = datetime.now() - timedelta(days=days)
        
        vehicles = Vehicle.objects.filter(
            group_id=group_id,
            is_active=True
        )
        
        registers = Register.objects.filter(
            vehicle__in=vehicles,
            created_at__gte=start_date
        )
        
        return {
            'group_id': group_id,
            'total_vehicles': vehicles.count(),
            'total_disconnections': registers.count(),
            'route_disconnections': registers.filter(
                disconnection_type=Register.DisconnectionType.DISCONNECTION_IN_ROUTE
            ).count(),
            'base_disconnections': registers.filter(
                disconnection_type=Register.DisconnectionType.DISCONNECTION_AT_BASE
            ).count(),
            'resolved': registers.filter(
                final_status=Register.FinalStatus.RESOLVED
            ).count(),
            'pending': registers.filter(
                final_status=Register.FinalStatus.PENDING
            ).count(),
            'avg_resolution_time': self._calculate_avg_resolution_time(registers)
        }
    
    def _calculate_avg_resolution_time(self, registers) -> float:
        """
        Calcula tiempo promedio de resolución.
        
        Args:
            registers: QuerySet de registros
        
        Returns:
            float: Horas promedio
        """
        resolved = registers.filter(
            final_status=Register.FinalStatus.RESOLVED
        )
        
        if not resolved.exists():
            return 0
        
        total_hours = 0
        for register in resolved:
            duration = register.updated_at - register.created_at
            total_hours += duration.total_seconds() / 3600
        
        return total_hours / resolved.count()
    
    def get_top_disconnection_vehicles(self, days: int = 30, 
                                      limit: int = 10) -> List[Dict]:
        """
        Obtiene vehículos con más desconexiones.
        
        Args:
            days: Número de días a analizar
            limit: Número máximo de resultados
        
        Returns:
            List[Dict]: Top vehículos
        """
        start_date = datetime.now() - timedelta(days=days)
        
        top_vehicles = Vehicle.objects.filter(
            registers__created_at__gte=start_date,
            is_active=True
        ).annotate(
            disconnection_count=Count('registers')
        ).order_by('-disconnection_count')[:limit]
        
        return [
            {
                'vin': v.vin,
                'vehicle_id': v.vehicle_id,
                'group': v.group.group_description,
                'disconnection_count': v.disconnection_count,
                'last_connection': v.last_connection
            }
            for v in top_vehicles
        ]
