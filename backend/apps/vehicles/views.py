"""
Views for Vehicles App
Handles Vehicle, Geofence, and Contrato endpoints
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vehicle, Geofence, Contrato
from .serializers import (
    VehicleSerializer,
    VehicleListSerializer,
    VehicleDetailSerializer,
    GeofenceSerializer,
    ContratoSerializer
)


class GeofenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Geofence management
    - list: Get all geofences
    - create: Create new geofence
    - retrieve: Get geofence details
    - update: Update geofence
    """
    
    queryset = Geofence.objects.all()
    serializer_class = GeofenceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['type', 'is_active']
    search_fields = ['name']
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a geofence"""
        geofence = self.get_object()
        geofence.is_active = True
        geofence.save()
        serializer = self.get_serializer(geofence)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a geofence"""
        geofence = self.get_object()
        geofence.is_active = False
        geofence.save()
        serializer = self.get_serializer(geofence)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def check_point(self, request, pk=None):
        """Check if a point is inside geofence"""
        geofence = self.get_object()
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if not all([latitude, longitude]):
            return Response(
                {'error': 'latitude and longitude required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            is_inside = geofence.is_point_inside(float(latitude), float(longitude))
            return Response({
                'geofence_id': geofence.id,
                'point': {'latitude': latitude, 'longitude': longitude},
                'is_inside': is_inside
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ContratoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Contrato management
    - list: Get all contracts
    - create: Create new contract
    - retrieve: Get contract details
    - update: Update contract
    """
    
    queryset = Contrato.objects.all().select_related('vehicle')
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['vehicle', 'is_active']
    search_fields = ['vin', 'contract_id']
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a contract"""
        contrato = self.get_object()
        contrato.is_active = True
        contrato.save()
        serializer = self.get_serializer(contrato)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a contract"""
        contrato = self.get_object()
        contrato.is_active = False
        contrato.save()
        serializer = self.get_serializer(contrato)
        return Response(serializer.data)


class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Vehicle management
    - list: Get all vehicles with pagination
    - create: Create new vehicle
    - retrieve: Get vehicle details
    - update: Update vehicle
    - partial_update: Update specific fields
    """
    
    queryset = Vehicle.objects.all().select_related(
        'group', 'distribuidor', 'geofence'
    ).prefetch_related('contrato_set')
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['group', 'distribuidor', 'geofence', 'is_connected']
    search_fields = ['vin', 'vehicle_id']
    ordering_fields = ['vehicle_id', 'vin', 'updated_at']
    ordering = ['-updated_at']
    pagination_class = None  # Will be set in settings
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return VehicleListSerializer
        elif self.action == 'retrieve':
            return VehicleDetailSerializer
        return self.serializer_class
    
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """Update vehicle location"""
        vehicle = self.get_object()
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if not all([latitude, longitude]):
            return Response(
                {'error': 'latitude and longitude required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            vehicle.latitude = float(latitude)
            vehicle.longitude = float(longitude)
            vehicle.save(update_fields=['latitude', 'longitude', 'updated_at'])
            serializer = self.get_serializer(vehicle)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def connect(self, request, pk=None):
        """Mark vehicle as connected"""
        vehicle = self.get_object()
        vehicle.is_connected = True
        vehicle.save(update_fields=['is_connected', 'updated_at'])
        serializer = self.get_serializer(vehicle)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def disconnect(self, request, pk=None):
        """Mark vehicle as disconnected"""
        vehicle = self.get_object()
        vehicle.is_connected = False
        vehicle.save(update_fields=['is_connected', 'updated_at'])
        serializer = self.get_serializer(vehicle)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def geofence_status(self, request, pk=None):
        """Check if vehicle is in its geofence"""
        vehicle = self.get_object()
        
        if not vehicle.geofence:
            return Response({
                'vehicle_id': vehicle.id,
                'has_geofence': False
            })
        
        try:
            is_in = vehicle.is_in_geofence()
            return Response({
                'vehicle_id': vehicle.id,
                'geofence_id': vehicle.geofence.id,
                'is_in_geofence': is_in
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
