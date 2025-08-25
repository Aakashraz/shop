"""
Patch for django-import-export-celery to fix 'str' object is not callable error
"""
from celery import shared_task
from import_export_celery.models import ImportJob
from importlib import import_module
import tablib
import logging
from django.utils import timezone



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

        logger.info(f"Looking for model: '{import_job.model}'")
        logger.info(f"Available configurations: {list(settings.IMPORT_EXPORT_CELERY_MODELS.keys())}")
        logger.info(f"Model split result: {import_job.model.split('.')}")

        if '.' in import_job.model:
            # Full path like "orders.Order"
            app_label, model_name = import_job.model.rsplit('.', 1)
            match_condition = lambda config: (config['app_label'] == app_label and
                                              config['model_name'] == model_name)
        else:
            # Just model name like "Order"
            model_name = import_job.model   # This gets "Captured" by the lambda
            match_condition = lambda config: config['model_name'] == model_name
            # Lambda now "remembers" that model_name = "Order"

        for config_key, config in settings.IMPORT_EXPORT_CELERY_MODELS.items():
            if match_condition(config):
                model_config = config
                logger.info(f"Found matching config: {config_key}")
                break
        # The above if match_condition(config):
        # This expands to:
        # if (lambda config: config['model_name'] == model_name)(config)
        # Which becomes:
        # if (lambda config: config['model_name'] == "Order")(config)
        # When we call it with config, it substitutes:
        # if config['model_name'] == "Order"
        # Which evaluates to:
        # "Order" == "Order"

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
        # Convert MIME type to tablib format
        format_mapping = {
            'text/csv': 'csv',
            'application/vnd.ms-excel': 'xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
            'text/plain': 'csv',    # Sometimes CSV is stored as text/plain
        }
        # THIS Maps MIME types(like 'text/csv') to tablib format names(like 'csv')
        # Falls back to the original format if no mapping exists

        # Get the correct format for tablib
        tablib_format = format_mapping.get(import_job.format, import_job.format)
        logger.info(f"Original format: '{import_job.format}', Using: '{tablib_format}'")
        # Use the converted format
        dataset.load(file_content, format=tablib_format)
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
            # Joins the first 5 error messages with semicolons and sets them to import_job.errors:

            import_job.job_status = "[Dry run] Import error" if dry_run else "Import error"
            # This import_job.job_status is not printed/logged because, django-import-export-celery
            # relies on the admin interface or queries to view job status (e.g. in a Django admin panel, users see status updates).

            logger.error(f"Import errors: {import_job.errors}")

        else:
            # Success
            totals = result.totals
            # Gets the import statistics dictionary (e.g., {'new': 3, 'update': 2, 'skip': 1}) from the result.

            summary_parts = []
            if totals.get('new', 0) > 0:
                # Checks if new records were created (defaults to 0 if key missing).
                summary_parts.append(f"Created: {totals['new']}")
            if totals.get('update', 0) > 0:
                summary_parts.append(f"Updated: {totals['update']}")
            if totals.get('skip', 0) > 0:
                summary_parts.append(f"Skipped: {totals['skip']}")

            import_job.change_summary = "; ".join(summary_parts) if summary_parts else "No changes"
            import_job.job_status = "[Dry run] Import finished" if dry_run else "Import finished"
            import_job.errors = ""  # Clears any previous errors on success.
            logger.info(f"Import successful: {import_job.change_summary}")


        # Mark as imported if not dry run
        if not dry_run:
            import_job.imported = timezone.now()    # Set completion timestamp
        else:
            import_job.imported = None  # Keep null for dry runs

        import_job.save()
        # Commits all changes to DB. Without this, updates are in-memory only -- task ends, changes disappear,
        # and admin sees nothing new.
        return {
            'success': True,
            'has_errors': result.has_errors(),
            'totals': result.totals,
            'row_count': len(dataset) if 'dataset' in locals() else 0,
            'dry_run': dry_run
        }

    except Exception as e:
        logger.error(f"Import job {pk} failed: {str(e)}")
        try:
            import_job = ImportJob.objects.get(pk=pk)
            import_job.errors = f"Import error: {str(e)}"
            import_job.job_status = "Import error"
            import_job.save()
        # "Refetches import_job because the outer exception might have occurred before import_job was fetched or
        # if DB issues arose. Ensures we can still update it."
        # "The main code might crash right at the start, before it even laods import_job from the database.
        # Without refetching, you'd have nothing to update."

        except:
            pass
        raise


# Replace the original task with our patched version
import import_export_celery.tasks
import_export_celery.tasks.run_import_job = patched_run_import_job

