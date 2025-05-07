# import celery
from .celery import app as celery_app


__all__ = ['celery_app']
# To explicitly expose the Celery app object when the project is imported.
# Explicitly exposes only celery_app from the myshop package for cleaner, controlled imports.