# backend/apps/vehicles/serializers.py

"""
Serializers for Vehicles App
Handles Vehicle, Geofence, and Contrato serialization
"""

from rest_framework import serializers
from .models import Vehicle, Geofence, Contrato
from apps.organization.serializers import GroupSerializer, DistribuidorSerializer

# ============================================================================
# HELPER SERIALIZERS
# ============================================================================
class GeofenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geofence
        fields = '__all__'

class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = '__all__'

# ============================================================================
# VEHICLE SERIALIZER (El bueno para los reportes)
# ============================================================================
class VehicleSerializer(serializers.ModelSerializer):
    # Traemos los nombres de las relaciones para no mandar solo IDs
    group_name = serializers.ReadOnlyField(source='group.group_description')
    distribuidor_name = serializers.ReadOnlyField(source='distribuidor.distribuidor_name')
    geofence_name = serializers.ReadOnlyField(source='geofence.geo_name')
    
    # AGREGAMOS LA MAGIA: Las propiedades calculadas en el Model
    connection_status = serializers.ReadOnlyField() # True/False
    disconnected_type = serializers.ReadOnlyField() # 'Base', 'Trayecto' o 'Conectado'

    class Meta:
        model = Vehicle
        fields = [
            'id', 'vehicle_id', 'vin', 'speed', 'last_connection',
            'group_name', 'distribuidor_name', 'geofence_name',
            'connection_status', 'disconnected_type', 
            'last_latitude', 'last_longitude'
        ]

    # Mantenemos las validaciones de VS Code porque están chidas
    def validate_vin(self, value):
        if len(value) != 17:
            raise serializers.ValidationError("El VIN debe tener 17 caracteres.")
        return value.upper()