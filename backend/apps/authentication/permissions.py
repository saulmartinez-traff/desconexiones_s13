"""
Permission Classes for Role-Based Access Control
"""

from rest_framework import permissions

class IsPMOrAdmin(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ['ADMIN', 'PM', 'DIRECTOR'] or request.user.is_superuser)
        
class IsDistribuidor(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'DISTRIBUIDOR'