"""
Organization App URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DistribuidorViewSet, ClientViewSet, GroupViewSet

router = DefaultRouter()
router.register(r'distribuidores', DistribuidorViewSet, basename='distribuidor')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'groups', GroupViewSet, basename='group')

urlpatterns = [
    path('', include(router.urls)),
]
