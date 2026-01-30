from django.contrib import admin
from .models import Register, Bitacora

@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'report_date', 'type', 'distribuidor')
    list_filter = ('report_date', 'type', 'distribuidor')
    search_fields = ('vehicle__vin', 'problem')

@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ('register', 'user', 'created_at')
    readonly_fields = ('created_at',)