"""
Views for Registers App
Handles Register and Bitacora endpoints
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Register, Bitacora
from .serializers import RegisterSerializer, BitacoraSerializer # Importamos SOLO lo que existe

class BitacoraViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista de solo lectura para la auditoría.
    """
    queryset = Bitacora.objects.all().select_related('register', 'user')
    serializer_class = BitacoraSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['register', 'user']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

class RegisterViewSet(viewsets.ModelViewSet):
    """
    Gestión de registros de desconexión.
    Incluye auditoría automática al crear/actualizar.
    """
    # Optimizamos la consulta trayendo vehículo y responsable
    queryset = Register.objects.all().select_related('vehicle', 'distribuidor').prefetch_related('bitacora_entries')
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Filtramos por fecha y tipo de problema (útil para reportes)
    filterset_fields = ['report_date', 'type', 'distribuidor', 'last_status']
    search_fields = ['vehicle__vin', 'problem', 'comentario']
    ordering_fields = ['report_date', 'created_at']
    ordering = ['-report_date']

    def perform_create(self, serializer):
        """
        Al crear, pasamos el usuario actual al contexto para que
        la Bitacora sepa quién hizo el cambio (si el serializer lo requiere).
        """
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Endpoint rápido para gráfica de pay: Conteo por estatus.
        """
        # Aquí puedes usar la lógica de agregación que aprendimos en vehicles
        # Ejemplo simple:
        from django.db.models import Count
        data = Register.objects.values('last_status').annotate(total=Count('id'))
        return Response(data)