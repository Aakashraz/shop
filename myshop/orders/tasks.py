from celery import shared_task
from django.core.mail import send_mail
from .models import Order

import logging
from importlib import import_module
from import_export_celery.tasks import run_import_job as original_import_job


logger = logging.getLogger(__name__)

@shared_task(bind=True)
def run_import_job(self, *args, **kwargs):
    from pprint import pformat
    print("RAW KWARGS FROM CELERY:")
    print(pformat(kwargs))
    ...


def get_resources_class(path):
    """
    Converts a resource string from settings.py  (e.g., 'orders.resources.OrderResource') to the actual class.
    If the resource is already a class, returns it as is.
    """
    if isinstance(path, str):
        try: 
            module_name, class_name = path.rsplit('.',1)
            module = import_module(module_name)
            resource_class = getattr(module, class_name)
            logger.debug(f"Resolved resource: {path} to {resource_class}")
            return resource_class
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to import resource: {path}. Error: {e}")
            raise
    return path


@shared_task
# def run_import_job(*args, **kwargs):    # You've deliberately given your new task the exact same name as
#     # the original one. When Celery starts, it will discover this task in your project and use it instead
#     # of the default one from the library. This is a powerful technique called overriding or monkey patching.
#     logger.info(f"Task args: {args}, kwargs: {kwargs}")
#
#     # Look for 'resource' in kwargs because Celery's import-export task usually has something like:
#     # run_import_job(dataset_id=..., resource="orders.resources.OrderResource")
#     # Convert resource string to class if necessary (as 'resource' is now an actual class object)
#     if 'resource' in kwargs:
#         kwargs['resource'] = get_resources_class(kwargs['resource'])
#
#     try:
#         result = original_import_job(*args, **kwargs)
#         logger.info(f"Task processed rows: {result or 'Unknown'}")
#     except Exception as e:
#         logger.error(f"Error in run_import_job: {e}")
#         raise   # Re-raise to let Celery handle retries or failures
#
#     return result

# It’s always recommended to only pass IDs to task functions and retrieve objects from the database
# when the task is executed. By doing so, we avoid accessing outdated information since the data
# in the database might have changed while the task was queued.


# @shared_task is a function decorator that tells Celery:
#   "Register this function as a Celery task that can be run asynchronously."
@shared_task
def order_created(order_id):
    """
    Task to send an e-mail notification when an order is successfully created.
    """
    order = Order.objects.get(id=order_id)
    subject = f'Order nr. {order.id}'
    message = (
        f'Dear {order.first_name},\n\n'
        f'You have successfully placed an order.'
        f'Your order ID is {order.id}'
    )
    mail_sent = send_mail(
        subject, message, 'admin@myshop.com', [order.email]
    )
    return mail_sent


# For test purpose only
# @shared_task()
# def test_task():
#     return "celery rocks"

# Another test method for celery import checking///////////////
# @shared_task
# def test_import():
#     print(f"OrderResource type: {type(OrderResource)}")
#     resource = OrderResource()
#     print("Resource instantiated successfully")
#     return "Test complete"

