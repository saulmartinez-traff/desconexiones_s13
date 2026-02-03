"""
Registers App URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterViewSet

router = DefaultRouter()
# Usar '' en lugar de 'registers' porque la URL padre ya incluye 'registers/'
router.register(r'', RegisterViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),
]
