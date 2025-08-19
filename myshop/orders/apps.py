from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        try:
            from . import celery_patch
            print('Celery patched loaded successfully')
        except ImportError as e:
            print(f"Celery patch failed to load: {e}")
