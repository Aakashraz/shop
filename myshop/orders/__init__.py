try:
    from . import celery_patch
    print("Celery patch loaded successfully")
except ImportError as e:
    print(f"Failed to load celery patch: {e}")