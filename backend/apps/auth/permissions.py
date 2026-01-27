"""
Permission Classes for Role-Based Access Control
"""

from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users"""
    
    message = "Only administrators can access this endpoint"
    
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == User.ADMIN
        )


class IsManager(permissions.BasePermission):
    """Allow access to managers and admins"""
    
    message = "Only managers or administrators can access this endpoint"
    
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in [User.ADMIN, User.MANAGER]
        )


class IsOperator(permissions.BasePermission):
    """Allow access to operators, managers and admins"""
    
    message = "Insufficient permissions"
    
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in [
                User.ADMIN, User.MANAGER, User.OPERATOR
            ]
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access to own profile or admins"""
    
    message = "You can only access your own profile"
    
    def has_object_permission(self, request, view, obj):
        return (
            obj.id == request.user.id or
            request.user.role == User.ADMIN
        )


class CanCreateRegister(permissions.BasePermission):
    """Allow operators, managers and admins to create registers"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in [
                User.ADMIN, User.MANAGER, User.OPERATOR
            ]
        )


class CanEditRegister(permissions.BasePermission):
    """Allow managers and admins to edit registers"""
    
    message = "Only managers or administrators can edit registers"
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in [User.ADMIN, User.MANAGER]
        )


class IsViewerOrAbove(permissions.BasePermission):
    """Allow viewers and above to read"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role != User.VIEWER
        )
