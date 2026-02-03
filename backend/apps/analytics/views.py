"""
Analytics Views
Provides aggregated data and analytics endpoints
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta

from apps.registers.models import Register
from apps.vehicles.models import Vehicle
from apps.organization.models import Group, Client


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def summary_matrix(request):
    """
    Endpoint para matriz de resumen - OPTIMIZADO
    Retorna datos agregados de vehículos conectados/desconectados
    organizados por grupo y contrato
    """
    from collections import defaultdict
    
    # Obtener parámetros de filtro
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')
    group_id = request.query_params.get('group_id')
    
    # Configurar rango de fechas
    if not end_date_str:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    
    if not start_date_str:
        start_date = end_date - timedelta(days=7)  # Reducir a 7 días por defecto
    else:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    
    # Generar lista de fechas
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    # Obtener grupos (con opción de filtro)
    groups_query = Group.objects.select_related('client')
    if group_id:
        groups_query = groups_query.filter(id=group_id)
    
    # Obtener todos los vehículos de una vez
    vehicles_query = Vehicle.objects.select_related('group', 'group__client')
    if group_id:
        vehicles_query = vehicles_query.filter(group_id=group_id)
    
    # Crear índice de vehículos por grupo y contrato
    vehicles_by_group_contract = defaultdict(lambda: defaultdict(list))
    for vehicle in vehicles_query:
        contract_key = vehicle.contrato if vehicle.contrato else 'null'
        vehicles_by_group_contract[vehicle.group_id][contract_key].append(vehicle.id)
    
    # Obtener todos los registros de desconexión en el rango de fechas de una vez
    registers = Register.objects.filter(
        report_date__gte=start_date,
        report_date__lte=end_date
    ).select_related('vehicle').values(
        'vehicle_id',
        'vehicle__group_id',
        'vehicle__contrato',
        'report_date',
        'problem'
    )
    
    # Crear índice de desconexiones por grupo, contrato y fecha
    disconnections_index = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'count': 0, 'route': 0, 'base': 0})))
    
    for register in registers:
        group_id = register['vehicle__group_id']
        contract_key = register['vehicle__contrato'] if register['vehicle__contrato'] else 'null'
        date_key = register['report_date']
        
        disconnections_index[group_id][contract_key][date_key]['count'] += 1
        
        if 'trayecto' in register['problem'].lower():
            disconnections_index[group_id][contract_key][date_key]['route'] += 1
        else:
            disconnections_index[group_id][contract_key][date_key]['base'] += 1
    
    # Construir respuesta
    groups_data = []
    
    for group in groups_query:
        group_matrix = {
            'group_name': group.group_description,
            'group_id': group.group_id,
            'client_name': group.client.client_description if group.client else None,
            'data': []
        }
        
        # Obtener contratos únicos del grupo
        contracts = vehicles_by_group_contract.get(group.id, {})
        
        for contract_key, vehicle_ids in contracts.items():
            contract_data = {
                'contract_name': f'Contrato {contract_key}' if contract_key != 'null' else 'Sin Contrato',
                'contract_id': contract_key if contract_key != 'null' else None,
                'daily_data': []
            }
            
            total_vehicles = len(vehicle_ids)
            
            # Procesar cada fecha
            for date in dates:
                # Obtener desconexiones de este grupo/contrato/fecha
                disconnections = disconnections_index[group.id][contract_key].get(date, {'count': 0, 'route': 0, 'base': 0})
                
                disconnected = disconnections['count']
                connected = total_vehicles - disconnected
                
                contract_data['daily_data'].append({
                    'date': date.strftime('%Y-%m-%d'),
                    'total': total_vehicles,
                    'connected': connected,
                    'disconnected': disconnected,
                    'route': disconnections['route'],
                    'base': disconnections['base'],
                    'percentage_connected': round((connected / total_vehicles * 100), 2) if total_vehicles > 0 else 0
                })
            
            group_matrix['data'].append(contract_data)
        
        groups_data.append(group_matrix)
    
    return Response({
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'dates': [d.strftime('%Y-%m-%d') for d in dates],
        'groups': groups_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_stats(request, group_id):
    """
    Estadísticas de un grupo específico
    """
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({'error': 'Grupo no encontrado'}, status=404)
    
    # Parámetros
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Obtener vehículos del grupo
    vehicles = Vehicle.objects.filter(group=group)
    total_vehicles = vehicles.count()
    
    # Obtener registros en el rango
    registers = Register.objects.filter(
        vehicle__in=vehicles,
        report_date__gte=start_date
    )
    
    total_disconnections = registers.count()
    
    # Contar por tipo de problema
    route_count = registers.filter(problem__icontains='trayecto').count()
    base_count = registers.filter(problem__icontains='base').count()
    
    # Contar por estatus
    status_counts = {}
    for choice_value, choice_label in Register.ESTATUS_CHOICES:
        count = registers.filter(estatus_final=choice_value).count()
        if count > 0:
            status_counts[choice_label] = count
    
    # Calcular tiempo promedio de resolución (aproximado)
    # Asumimos que si updated_at != created_at, fue resuelto
    resolved_registers = registers.exclude(updated_at=F('created_at'))
    avg_resolution_hours = 0
    if resolved_registers.exists():
        total_seconds = sum([
            (r.updated_at - r.created_at).total_seconds()
            for r in resolved_registers
        ])
        avg_resolution_hours = round(total_seconds / 3600 / resolved_registers.count(), 2)
    
    return Response({
        'group_id': group.id,
        'group_name': group.group_description,
        'client_name': group.client.client_description if group.client else None,
        'total_vehicles': total_vehicles,
        'total_disconnections': total_disconnections,
        'disconnected_route': route_count,
        'disconnected_base': base_count,
        'status_breakdown': status_counts,
        'avg_resolution_hours': avg_resolution_hours,
        'period_days': days
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_disconnected_vehicles(request):
    """
    Vehículos con más desconexiones
    """
    limit = int(request.query_params.get('limit', 10))
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Contar desconexiones por vehículo
    top_vehicles = Vehicle.objects.filter(
        registers__report_date__gte=start_date
    ).annotate(
        disconnection_count=Count('registers')
    ).select_related('group', 'group__client').order_by('-disconnection_count')[:limit]
    
    vehicles_data = []
    for vehicle in top_vehicles:
        vehicles_data.append({
            'vin': vehicle.vin,
            'vehicle_id': vehicle.vehicle_id,
            'group': vehicle.group.group_description if vehicle.group else None,
            'client': vehicle.group.client.client_description if vehicle.group and vehicle.group.client else None,
            'disconnection_count': vehicle.disconnection_count,
            'last_connection': vehicle.last_connection.isoformat() if vehicle.last_connection else None
        })
    
    return Response({
        'period_days': days,
        'limit': limit,
        'vehicles': vehicles_data
    })
