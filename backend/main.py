import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from services.etl_service import ETLService

def main():
    print("=== Iniciando ETL ===")
    
    # Configurar URL de la API
    # Puedes obtenerla de variables de entorno o hardcodearla para pruebas
    api_url = os.getenv('TELEMETRY_API_URL')
    
    # Crear instancia del servicio
    etl = ETLService(api_url=api_url)
    
    try:
        # Ejecutar ETL con límite de 1 página para pruebas
        # Para producción, omite el parámetro o pon un número grande
        stats = etl.run_etl(max_pages=2)
        
        print("\n=== Resumen del Proceso ===")
        print(f"Registros procesados: {stats['total_records']}")
        print(f"Clientes creados: {stats['clients_created']}")
        print(f"Grupos creados: {stats['groups_created']}")
        print(f"Geocercas creadas: {stats['geofences_created']}")
        print(f"Vehículos creados: {stats['vehicles_created']}")
        print(f"Vehículos actualizados: {stats['vehicles_updated']}")
        print(f"Registros creados: {stats['registers_created']}")
        print(f"Desconexiones en ruta: {stats['disconnections_route']}")
        print(f"Desconexiones en base: {stats['disconnections_base']}")
        print(f"Errores: {stats['errors']}")
        
    except Exception as e:
        print(f"\n=== Error Crítico ===")
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
