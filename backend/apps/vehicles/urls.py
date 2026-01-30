"""
Vehicles App URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, GeofenceViewSet, ContratoViewSet

router = DefaultRouter()
router.register(r'data', VehicleViewSet, basename='vehicle')
router.register(r'geofences', GeofenceViewSet, basename='geofence')
router.register(r'contratos', ContratoViewSet, basename='contrato')

urlpatterns = [
    path('', include(router.urls)),
]
