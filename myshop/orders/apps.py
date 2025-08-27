from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        try:
            from . import celery_patch
            print('Celery patched loaded successfully')
        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not lead celery_patch: {e}")