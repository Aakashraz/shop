"""
Patch for django-import-export-celery to fix 'str' object is not callable error
"""
from celery import shared_task
from import_export_celery.models import ImportJob
from importlib import import_module
import tablib
import logging


logger = logging.getLogger(__name__)

@shared_task
def patched_run_import_job(pk, dry_run=True):
    """
    Patched version of run_import_job that handles serialization properly
    """
    try:
        import_job = ImportJob.objects.get(pk=pk)
        logger.info(f"Processing import job {pk}, dry_run={dry_run}")

        # Get the resource class from the settings