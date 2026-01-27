"""
Serializers for Registers App
Handles Register and Bitacora serialization with audit trail
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Register, Bitacora
from apps.vehicles.serializers import VehicleListSerializer
from apps.organization.serializers import UserSerializer

User = get_user_model()


class BitacoraSerializer(serializers.ModelSerializer):
    """Serializer for Bitacora (audit trail) model"""
    
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User,
        source='user',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Bitacora
        fields = [
            'id', 'register', 'user', 'user_id', 'comentario',
            'created_at'
        ]
        read_only_fields = ['id', 'register', 'created_at']


class RegisterListSerializer(serializers.ModelSerializer):
    """List Serializer for Register (simplified view)"""
    
    vehicle = VehicleListSerializer(read_only=True)
    
    class Meta:
        model = Register
        fields = [
            'id', 'vehicle', 'report_date', 'problem', 'type',
            'last_status', 'updated_at'
        ]
        read_only_fields = fields


class RegisterDetailSerializer(serializers.ModelSerializer):
    """Detailed Serializer for Register with audit trail"""
    
    vehicle = VehicleListSerializer(read_only=True)
    vehicle_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.vehicles.models', fromlist=['Vehicle']).Vehicle,
        source='vehicle',
        write_only=True,
        required=True
    )
    
    bitacora = BitacoraSerializer(many=True, read_only=True)
    
    class Meta:
        model = Register
        fields = [
            'id', 'vehicle', 'vehicle_id', 'report_date',
            'platform_client', 'distribuidor', 'last_connection',
            'problem', 'type', 'last_status', 'comentario',
            'bitacora', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'report_date', 'bitacora',
            'created_at', 'updated_at'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """Main Serializer for Register model"""
    
    vehicle_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.vehicles.models', fromlist=['Vehicle']).Vehicle,
        source='vehicle',
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Register
        fields = [
            'id', 'vehicle_id', 'report_date',
            'platform_client', 'distribuidor', 'last_connection',
            'problem', 'type', 'last_status', 'comentario',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'report_date', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """Create register"""
        register = Register.objects.create(**validated_data)
        
        # Log creation to bitacora
        Bitacora.log_action(
            register=register,
            user=self.context['request'].user if 'request' in self.context else None,
            comentario='Registro creado'
        )
        
        return register
    
    def update(self, instance, validated_data):
        """Update register and log to bitacora"""
        # Track changes for audit
        changes = {}
        for field, value in validated_data.items():
            old_value = getattr(instance, field.replace('_id', ''), None)
            if old_value != value:
                changes[field] = (old_value, value)
        
        # Update instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Log changes to bitacora if there are changes
        if changes:
            change_summary = ', '.join([f'{field}: {old} → {new}' for field, (old, new) in changes.items()])
            Bitacora.log_action(
                register=instance,
                user=self.context['request'].user if 'request' in self.context else None,
                comentario=f'Registro actualizado: {change_summary}'
            )
        
        return instance


class RegisterCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Register"""
    
    vehicle_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.vehicles.models', fromlist=['Vehicle']).Vehicle,
        source='vehicle',
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Register
        fields = [
            'id', 'vehicle_id', 'report_date',
            'platform_client', 'distribuidor', 'last_connection',
            'problem', 'type', 'last_status', 'comentario', 'created_at'
        ]
        read_only_fields = [
            'id', 'report_date', 'created_at'
        ]
    
    def create(self, validated_data):
        """Create register"""
        register = Register.objects.create(**validated_data)
        
        # Log creation to bitacora
        Bitacora.log_action(
            register=register,
            user=self.context['request'].user if 'request' in self.context else None,
            comentario='Registro creado'
        )
        
        return register

