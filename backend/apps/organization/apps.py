"""
Organization App Configuration
"""

from django.apps import AppConfig


class OrganizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.organization'
    verbose_name = 'Organization Management'

    def ready(self):
        """Importar signals cuando la app esté lista"""
        pass
