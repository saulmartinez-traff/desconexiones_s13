# backend/apps/organization/serializers.py

"""
Serializers for Organization App
Handles User, Distribuidor, Client, and Group serialization
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Distribuidor, Client, Group

User = get_user_model()

# ============================================================================
# USER SERIALIZER
# ============================================================================
class UserSerializer(serializers.ModelSerializer):
    """Serializer para el usuario personalizado heredado de AbstractUser"""
    
    # Queremos ver el nombre del distribuidor, no solo el ID
    distribuidor_name = serializers.ReadOnlyField(source='distribuidor.distribuidor_name')

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'distribuidor', 'distribuidor_name', 'is_staff', 'role'
        ]
        # El password no se debe enviar de vuelta nunca
        extra_kwargs = {'password': {'write_only': True}}

# ============================================================================
# DISTRIBUIDOR SERIALIZER
# ============================================================================
class DistribuidorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribuidor
        fields = '__all__' # Para rápido, ya que son pocos campos

# ============================================================================
# CLIENT & GROUP SERIALIZERS
# ============================================================================
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    # Esto es un "Nested Serializer". Cuando pidas un grupo, 
    # te traerá toda la info del cliente de una vez. ¡Súper útil para React!
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), 
        source='client', 
        write_only=True
    )

    class Meta:
        model = Group
        fields = ['id', 'group_id', 'group_description', 'client', 'client_id']