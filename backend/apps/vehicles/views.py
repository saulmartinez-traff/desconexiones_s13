# backend/apps/vehicles/views.py

"""
Views for Vehicles App
Handles Vehicle, Geofence, and Contrato endpoints
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from rest_framework.decorators import action
from django.utils import timezone
from .models import Vehicle, Geofence, Contrato
from .serializers import VehicleSerializer, GeofenceSerializer, ContratoSerializer
from apps.authentication.permissions import IsPMOrAdmin

class VehicleViewSet(viewsets.ModelViewSet):
    """
    Punto de entrada para los vehículos.
    Solo muestra los vehículos que pertenecen al distribuidor del usuario.
    """
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtros para tus reportes dinámicos
    filterset_fields = ['group', 'geofence', 'distribuidor'] 
    search_fields = ['vin', 'vehicle_id']
    ordering_fields = ['last_connection', 'speed']

    def get_queryset(self):
        """
        MAGIA DE SEGURIDAD: 
        Filtramos la base de datos según el usuario logueado.
        """
        user = self.request.user
        queryset = Vehicle.objects.all().select_related('group', 'distribuidor', 'geofence')

        # Si el usuario NO es superusuario, solo ve su distribuidor
        if not user.is_superuser and user.distribuidor:
            return queryset.filter(distribuidor=user.distribuidor)
        
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[IsPMOrAdmin])
    def statistics(self, request):
        
        user = self.request.user
        hoy = timezone.now().date()
        
        queryset = self.get_queryset()
        
        stats = queryset.aggregate(
            total=Count('id'),
            conectados=Count('id', filter=Q(last_connection__date=hoy)),
            desconectados=Count('id', filter=Q(last_connection__date__lt=hoy) | Q(last_connection__isnull=True)),
            desconectados_trayecto=Count('id', filter=Q(last_connection__date__lt=hoy) & Q(speed__gt=0)),
            desconectados_base=Count('id', filter=Q(last_connection__date__lt=hoy) & Q(speed__lte=0))
        )
        return Response(stats)

# Simplificamos los otros ViewSets
class GeofenceViewSet(viewsets.ModelViewSet):
    queryset = Geofence.objects.all()
    serializer_class = GeofenceSerializer
    permission_classes = [IsAuthenticated]

class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]

