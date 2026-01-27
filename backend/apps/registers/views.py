"""
Views for Registers App
Handles Register and Bitacora endpoints
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from django.utils import timezone
from .models import Register, Bitacora
from .serializers import (
    RegisterSerializer,
    RegisterListSerializer,
    RegisterDetailSerializer,
    RegisterCreateSerializer,
    BitacoraSerializer
)


class BitacoraViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for Bitacora (audit trail)
    - list: Get all audit entries
    - retrieve: Get specific audit entry
    """
    
    queryset = Bitacora.objects.all().select_related('register', 'user')
    serializer_class = BitacoraSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['register', 'action', 'user']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def by_register(self, request):
        """Get audit trail for a specific register"""
        register_id = request.query_params.get('register_id')
        
        if not register_id:
            return Response(
                {'error': 'register_id query parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bitacora = Bitacora.objects.filter(register_id=register_id)
        serializer = self.get_serializer(bitacora, many=True)
        return Response(serializer.data)


class RegisterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Register management
    - list: Get all disconnection records
    - create: Create new record
    - retrieve: Get record details
    - update: Update record (with audit)
    - partial_update: Partial update
    """
    
    queryset = Register.objects.all().select_related(
        'vehicle', 'responsible'
    ).prefetch_related('bitacora_set')
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'vehicle', 'disconnection_type', 'problem_type',
        'final_status', 'responsible'
    ]
    search_fields = ['vehicle__vin', 'vehicle__vehicle_id', 'problem']
    ordering_fields = ['report_date', 'created_at', 'updated_at']
    ordering = ['-report_date']
    pagination_class = None
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return RegisterListSerializer
        elif self.action == 'retrieve':
            return RegisterDetailSerializer
        elif self.action == 'create':
            return RegisterCreateSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Log register creation to bitacora"""
        instance = serializer.save()
        Bitacora.log_action(
            register=instance,
            action=Bitacora.CREATE,
            user=self.request.user
        )
    
    def perform_update(self, serializer):
        """Log register updates to bitacora"""
        instance = serializer.save()
        Bitacora.log_action(
            register=instance,
            action=Bitacora.UPDATE,
            user=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def assign_to(self, request, pk=None):
        """Assign register to a user"""
        register = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not register.is_editable():
            return Response(
                {'error': 'Cannot modify register older than 7 days'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            
            register.responsible = user
            register.save(update_fields=['responsible', 'updated_at'])
            
            Bitacora.log_action(
                register=register,
                action=Bitacora.ASSIGNED,
                user=request.user,
                field_name='responsible',
                old_value=getattr(register.responsible, 'username', 'None'),
                new_value=user.username
            )
            
            serializer = self.get_serializer(register)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add comment to register"""
        register = self.get_object()
        comment = request.data.get('comment')
        
        if not comment:
            return Response(
                {'error': 'comment required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not register.is_editable():
            return Response(
                {'error': 'Cannot modify register older than 7 days'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_comment = register.comment or ''
        register.comment = comment
        register.save(update_fields=['comment', 'updated_at'])
        
        Bitacora.log_action(
            register=register,
            action=Bitacora.COMMENT,
            user=request.user,
            field_name='comment',
            old_value=old_comment,
            new_value=comment
        )
        
        serializer = self.get_serializer(register)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        """Update final_status of register"""
        register = self.get_object()
        new_status = request.data.get('final_status')
        
        if not new_status:
            return Response(
                {'error': 'final_status required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not register.is_editable():
            return Response(
                {'error': 'Cannot modify register older than 7 days'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = register.final_status
        register.final_status = new_status
        register.save(update_fields=['final_status', 'updated_at'])
        
        Bitacora.log_action(
            register=register,
            action=Bitacora.STATUS,
            user=request.user,
            field_name='final_status',
            old_value=old_status,
            new_value=new_status
        )
        
        serializer = self.get_serializer(register)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def editable(self, request):
        """Get only editable registers (< 7 days old)"""
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)
        
        editable = Register.objects.filter(created_at__gte=seven_days_ago)
        
        # Apply filters
        serializer = RegisterListSerializer(editable, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get registers grouped by status"""
        status_counts = {}
        
        for status_choice in Register.FINAL_STATUS_CHOICES:
            status_value = status_choice[0]
            status_label = status_choice[1]
            count = Register.objects.filter(final_status=status_value).count()
            status_counts[status_label] = count
        
        return Response(status_counts)
