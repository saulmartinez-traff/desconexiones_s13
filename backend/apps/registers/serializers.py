# backend/apps/registers/serializers.py

from rest_framework import serializers
from .models import Register, Bitacora

# ============================================================================
# BITACORA SERIALIZER (¡Este faltaba!)
# ============================================================================
class BitacoraSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField() # Para que salga el nombre, no el ID
    class Meta:
        model = Bitacora
        fields = '__all__'

# ============================================================================
# REGISTER SERIALIZER (El "Aplanado")
# ============================================================================
class RegisterSerializer(serializers.ModelSerializer):
    # --- Campos traídos desde Vehículo ---
    vin = serializers.ReadOnlyField(source='vehicle.vin')
    vehicle_id = serializers.ReadOnlyField(source='vehicle.vehicle_id')
    
    # --- Campos de Organización (Navegamos las relaciones) ---
    distribuidor_name = serializers.SerializerMethodField()
    client_description = serializers.SerializerMethodField()
    
    # --- Campo calculado ---
    contrato = serializers.SerializerMethodField()

    class Meta:
        model = Register
        fields = [
            'id', 'created_at', 'updated_at', 'report_date', 
            'vin', 'vehicle_id', 
            'client_description', 'distribuidor_name', 'contrato', 
            'last_connection', 'problem', 
            'tipo', 'estatus_final', 'responsable', 'comentario'
        ]
        read_only_fields = ['created_at', 'updated_at', 'report_date']

    def get_distribuidor_name(self, obj):
        """Obtener nombre del distribuidor desde el vehículo"""
        try:
            if obj.vehicle and obj.vehicle.distribuidor:
                return obj.vehicle.distribuidor.distribuidor_name
            return None
        except:
            return None

    def get_client_description(self, obj):
        """Obtener descripción del cliente desde el grupo del vehículo"""
        try:
            if obj.vehicle and obj.vehicle.group and obj.vehicle.group.client:
                return obj.vehicle.group.client.client_description
            return None
        except:
            return None

    def get_contrato(self, obj):
        """Verificar si el vehículo tiene contrato"""
        try:
            return "SÍ" if getattr(obj.vehicle, 'contrato', None) else "NO"
        except:
            return "NO"
