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
    last_connection = serializers.ReadOnlyField(source='vehicle.last_connection')
    
    # --- Campos de Organización (Navegamos las relaciones) ---
    # Nota: Usamos getattr en la vista o source seguro para evitar errores si es null
    distribuidor = serializers.ReadOnlyField(source='vehicle.distribuidor.distribuidor_name')
    cliente = serializers.ReadOnlyField(source='vehicle.group.client.client_description')
    
    # --- Campo calculado ---
    contrato = serializers.SerializerMethodField()

    class Meta:
        model = Register
        fields = [
            'id', 'report_date', 'vin', 'vehicle_id', 
            'cliente', 'distribuidor', 'contrato', 
            'last_connection', 'problem', 
            'type', 'final_status', 'responsible', 'comment'
        ]

    def get_contrato(self, obj):
        # Lógica temporal: si el vehículo tiene contrato, ponemos SÍ
        # Usamos getattr por seguridad si la relación no existe aún
        try:
            return "SÍ" if getattr(obj.vehicle, 'contrato', None) else "NO"
        except:
            return "NO"