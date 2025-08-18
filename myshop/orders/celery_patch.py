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
        from django.conf import settings
        model_config = None

        for model_name, config in settings.IMPORT_EXPORT_CELERY_MODELS.items():
            # import_job.model is a string from the ImportJob model,
            # typically in the format app_label.ModelName (e.g., orders.Order).
            # .split('.') splits this string into a list, e.g., ['orders', 'Order']
            if config['app_label'] == import_job.model.split('.')[0] and config['model_name'] == import_job.model.split('.')[-1]:
                model_config = config   # This ensures the config corresponds to the model being imported.
                break

        if not model_config:
            raise ValueError(f"No configuration found for model {import_job.model}")

        # Import the resource class
        resource_path = model_config['resource']
        module_name, class_name = resource_path.rsplit('.', 1)
        module = import_module(module_name)
        resource_class = getattr(module, class_name)

        # Create resource instance
        resource = resource_class()
        logger.info(f"Created resource class: {resource_class}")

        # Read the file content
        with import_job.file.open('r') as f:
            file_content = f.read()

        # create dataset
        dataset = tablib.Dataset()
        dataset.load(file_content, format=import_job.format)
        logger.info(f"Loaded dataset with {len(dataset)} rows")

        # Import the data
        result = resource.import_data(dataset, dry_run=dry_run)
        logger.info(f"Import result - has errors: {result.has_errors()}")

        # Update job status based on results
        if result.has_errors():
            error_message = []
            for row_errors in result.row_errors():
                error_message.append(f"Row {row_errors[0]}: {row_errors[1]}")

            import_job.errors = "; ".join(error_message[:5])    # Limit to first five errors
            import_job.job_status = "[Dry run] Import error" if dry_run else "Import error"
            logger.error(f"Import errors: {import_job.errors}")

        else:
            # Success
            totals = result.totals
            summary_parts = []
            if totals.get('new', 0) > 0:
                summary_parts.append(f"Created: {totals['new']}")
            if totals.get('update', 0) > 0:
                summary_parts.append(f"Updated: {totals['update']}")
            if totals.get('skip', 0) > 0:
                summary_parts.append(f"Skipped: {totals['skip']}")

            import_job.change_summary = "; ".join(summary_parts) if summary_parts else "No changes"
            import_job.job_status = "[Dry run] Import finished" if dry_run else "Import finished"
            import_job.errors = ""
            logger.info(f"Import successful: {import_job.change_summary}")


        # Mark as imported if not dry run
        if not dry_run:
            import_job.imported = True

        import_job.save()
        return result

    except Exception as e:
        logger.error(f"Import job {pk} failed: {str(e)}")
        try:
            import_job = ImportJob.objects.get(pk=pk)
            import_job.errors = f"Import error: {str(e)}"
            import_job.job_status = "Import error"
            import_job.save()
        except:
            pass
        raise


# Replace the original task with our patched version
import import_export_celery.tasks
import_export_celery.tasks.run_import_job = patched_run_import_job

