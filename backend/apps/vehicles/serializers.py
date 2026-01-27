"""
Serializers for Vehicles App
Handles Vehicle, Geofence, and Contrato serialization
"""

from rest_framework import serializers
from .models import Vehicle, Geofence, Contrato
from apps.organization.serializers import GroupSerializer, DistribuidorSerializer


class GeofenceSerializer(serializers.ModelSerializer):
    """Serializer for Geofence model"""
    
    class Meta:
        model = Geofence
        fields = ['id', 'geo_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContratoSerializer(serializers.ModelSerializer):
    """Serializer for Contrato model"""
    
    class Meta:
        model = Contrato
        fields = ['id', 'contrato_id', 'vin', 'contrato', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class VehicleListSerializer(serializers.ModelSerializer):
    """List Serializer for Vehicle (simplified view)"""
    
    group_name = serializers.CharField(source='group.group_description', read_only=True)
    distribuidor_name = serializers.CharField(
        source='distribuidor.distribuidor_name', read_only=True
    )
    geofence_name = serializers.CharField(source='geofence.geo_name', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'vehicle_id', 'vin', 'last_latitude', 'last_longitude',
            'group_name', 'distribuidor_name', 'geofence_name',
            'last_connection', 'updated_at'
        ]
        read_only_fields = fields


class VehicleDetailSerializer(serializers.ModelSerializer):
    """Detailed Serializer for Vehicle with full relationships"""
    
    group = GroupSerializer(read_only=True)
    distribuidor = DistribuidorSerializer(read_only=True)
    geofence = GeofenceSerializer(read_only=True)
    contrato = ContratoSerializer(read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'vehicle_id', 'vin', 'inner_id', 'last_latitude', 'last_longitude',
            'group', 'distribuidor', 'geofence', 'contrato', 'last_connection',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VehicleSerializer(serializers.ModelSerializer):
    """Main Serializer for Vehicle model"""
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'vehicle_id', 'vin', 'inner_id', 'last_latitude', 'last_longitude',
            'group', 'distribuidor', 'geofence', 'contrato', 'last_connection',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_vin(self, value):
        """Validate VIN format"""
        if len(value) != 17:
            raise serializers.ValidationError("VIN must be 17 characters long")
        if not value.isalnum():
            raise serializers.ValidationError("VIN must be alphanumeric")
        return value.upper()
    
    def validate(self, data):
        """Validate coordinate ranges"""
        latitude = data.get('last_latitude')
        longitude = data.get('last_longitude')
        
        if latitude is not None:
            if not (-90 <= float(latitude) <= 90):
                raise serializers.ValidationError(
                    {"last_latitude": "Must be between -90 and 90"}
                )
        
        if longitude is not None:
            if not (-180 <= float(longitude) <= 180):
                raise serializers.ValidationError(
                    {"last_longitude": "Must be between -180 and 180"}
                )
        
        return data
