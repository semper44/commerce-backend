from django.apps import AppConfig


class ProductappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'productapp'

    def ready(self):
        import productapp.signals