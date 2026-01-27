"""
Registers App URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterViewSet, BitacoraViewSet

router = DefaultRouter()
router.register(r'registers', RegisterViewSet, basename='register')
router.register(r'bitacora', BitacoraViewSet, basename='bitacora')

urlpatterns = [
    path('', include(router.urls)),
]
