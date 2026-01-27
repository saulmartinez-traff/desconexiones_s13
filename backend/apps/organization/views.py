"""
Views for Organization App
Handles User, Distribuidor, Client, and Group endpoints
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import Distribuidor, Client, Group
from .serializers import (
    UserSerializer,
    DistribuidorSerializer,
    ClientSerializer,
    GroupSerializer,
    GroupListSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management
    - list: Get all users (admins only)
    - create: Create new user (admins only)
    - retrieve: Get user details
    - update: Update user info
    - partial_update: Partial update
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    def get_queryset(self):
        """Filter users based on permissions"""
        user = self.request.user
        
        # Admins can see all users
        if user.role == User.ADMIN:
            return User.objects.all()
        
        # Others can only see themselves
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        """Set/change user password"""
        user = self.get_object()
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'detail': 'Password updated successfully'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DistribuidorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Distribuidor management
    - list: Get all distribuidores
    - create: Create new distribuidor (admins only)
    - retrieve: Get distribuidor details
    - update: Update distribuidor
    """
    
    queryset = Distribuidor.objects.all()
    serializer_class = DistribuidorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'distribuidor_id', 'contact_email']
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a distribuidor"""
        distribuidor = self.get_object()
        distribuidor.is_active = True
        distribuidor.save()
        serializer = self.get_serializer(distribuidor)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a distribuidor"""
        distribuidor = self.get_object()
        distribuidor.is_active = False
        distribuidor.save()
        serializer = self.get_serializer(distribuidor)
        return Response(serializer.data)


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Client management
    - list: Get all clients
    - create: Create new client
    - retrieve: Get client details
    - update: Update client
    """
    
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['distribuidor', 'is_active']
    search_fields = ['name', 'client_id', 'contact_email']
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a client"""
        client = self.get_object()
        client.is_active = True
        client.save()
        serializer = self.get_serializer(client)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a client"""
        client = self.get_object()
        client.is_active = False
        client.save()
        serializer = self.get_serializer(client)
        return Response(serializer.data)


class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Group management
    - list: Get all groups
    - create: Create new group
    - retrieve: Get group details
    - update: Update group
    """
    
    queryset = Group.objects.all().select_related('client')
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['client', 'is_active']
    search_fields = ['name', 'group_id', 'client__name']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return GroupListSerializer
        elif self.action == 'retrieve':
            return GroupSerializer
        return self.serializer_class
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a group"""
        group = self.get_object()
        group.is_active = True
        group.save()
        serializer = self.get_serializer(group)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a group"""
        group = self.get_object()
        group.is_active = False
        group.save()
        serializer = self.get_serializer(group)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def vehicle_count(self, request, pk=None):
        """Get vehicle count for group"""
        group = self.get_object()
        return Response({
            'group_id': group.id,
            'vehicle_count': group.vehicle_count
        })
