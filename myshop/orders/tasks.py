from celery import shared_task
from django.core.mail import send_mail
from .models import Order


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