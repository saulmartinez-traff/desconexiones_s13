"""
Serializers for Organization App
Handles User, Distribuidor, Client, and Group serialization
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Distribuidor, Client, Group

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = [
            'id', 'user_name', 'user_pass', 'user_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'user_pass': {'write_only': True},
        }
    
    def create(self, validated_data):
        """Create user with hashed password"""
        password = validated_data.pop('user_pass', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        """Update user, handling password separately"""
        password = validated_data.pop('user_pass', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password is not None:
            instance.set_password(password)
        
        instance.save()
        return instance


class DistribuidorSerializer(serializers.ModelSerializer):
    """Serializer for Distribuidor model"""
    
    class Meta:
        model = Distribuidor
        fields = [
            'id', 'distribuidor_id', 'distribuidor_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_distribuidor_id(self, value):
        """Validate distribuidor_id is unique"""
        if self.instance is None:  # Create operation
            if Distribuidor.objects.filter(distribuidor_id=value).exists():
                raise serializers.ValidationError(
                    "Distribuidor with this ID already exists"
                )
        return value


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model"""
    
    class Meta:
        model = Client
        fields = [
            'id', 'client_id', 'client_description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_client_id(self, value):
        """Validate client_id is unique"""
        if self.instance is None:  # Create operation
            if Client.objects.filter(client_id=value).exists():
                raise serializers.ValidationError(
                    "Client with this ID already exists"
                )
        return value


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Group model"""
    
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source='client',
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Group
        fields = [
            'id', 'group_id', 'group_description', 'client', 'client_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'client', 'created_at', 'updated_at']
    
    def validate_group_id(self, value):
        """Validate group_id is unique"""
        if self.instance is None:  # Create operation
            if Group.objects.filter(group_id=value).exists():
                raise serializers.ValidationError(
                    "Group with this ID already exists"
                )
        return value


class GroupListSerializer(serializers.ModelSerializer):
    """List Serializer for Group (simplified)"""
    
    client_description = serializers.CharField(source='client.client_description', read_only=True)
    
    class Meta:
        model = Group
        fields = [
            'id', 'group_id', 'group_description', 'client_id',
            'client_description', 'created_at'
        ]
        read_only_fields = fields
