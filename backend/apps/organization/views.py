# backend/apps/organization/views.py

"""
Views for Organization App
Handles User, Distribuidor, Client, and Group endpoints
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import Distribuidor, Client, Group
# Importamos SOLO lo que sí existe en tu serializers.py
from .serializers import (
    UserSerializer,
    DistribuidorSerializer,
    ClientSerializer,
    GroupSerializer
)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    Gestión de usuarios.
    - Admins ven todo.
    - Los demás solo ven su propio perfil.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # Quitamos 'is_active' porque no lo estamos usando explícitamente en el admin aún
    filterset_fields = ['role', 'distribuidor'] 
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    def get_queryset(self):
        """
        Filtra usuarios según permisos.
        """
        user = self.request.user
        
        # Si no está autenticado (aunque permission_classes lo evita), retornamos vacío
        if not user.is_authenticated:
            return User.objects.none()

        # Si es Admin o Superuser, ve todo
        if user.is_superuser or getattr(user, 'role', '') == 'ADMIN':
            return User.objects.all()
        
        # Los mortales solo se ven a sí mismos
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener perfil del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class DistribuidorViewSet(viewsets.ModelViewSet):
    queryset = Distribuidor.objects.all()
    serializer_class = DistribuidorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['distribuidor_name', 'distribuidor_id']


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['client_description', 'client_id']


class GroupViewSet(viewsets.ModelViewSet):
    # Usamos select_related para optimizar la consulta al cliente
    queryset = Group.objects.all().select_related('client')
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['client']
    search_fields = ['group_description', 'group_id']