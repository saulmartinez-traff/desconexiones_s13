# backend/core/urls.py

"""
Main URL configuration for desconexiones_s13 project.
Routes for JWT authentication, API v1 endpoints with app routers
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Authentication (JWT)
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # API v1 Routes
    path('api/v1/organization/', include('apps.organization.urls')),
    path('api/v1/vehicles/', include('apps.vehicles.urls')),
    path('api/v1/registers/', include('apps.registers.urls')),
    # path('api/v1/auth/', include('apps.authentication.urls')),
]
