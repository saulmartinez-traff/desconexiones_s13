from django.contrib import admin
from .models import Geofence, Contrato, Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    # Mostramos las propiedades calculadas como si fueran campos reales
    list_display = ('vin', 'distribuidor', 'speed', 'last_connection', 'connection_status_display')
    list_filter = ('distribuidor', 'geofence', 'group')
    search_fields = ('vin', 'vehicle_id')
    readonly_fields = ('connection_status_display',)

    def connection_status_display(self, obj):
        return "🔴 Desconectado" if obj.connection_status else "🟢 Conectado"
    
    connection_status_display.short_description = 'Estado Actual'

admin.site.register(Geofence)
admin.site.register(Contrato)