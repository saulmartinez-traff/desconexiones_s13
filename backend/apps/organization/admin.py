from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Distribuidor, Client, Group

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'distribuidor', 'is_staff')
    list_filter = ('role', 'distribuidor', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informacion Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Información de Rol y Negocio', {'fields': ('role', 'distribuidor')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información de Rol y Negocio', {'fields': ('role', 'distribuidor')}),
    )

@admin.register(Distribuidor)
class DistribuidorAdmin(admin.ModelAdmin):
    list_display = ('distribuidor_id', 'distribuidor_name')
    search_fields = ('distribuidor_name',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'client_description')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('group_id', 'group_description', 'client')
    list_filter = ('client',)