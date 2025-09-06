from io import BytesIO
import weasyprint
from celery import shared_task
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from orders.models import Order


@shared_task
def payment_completed(order_id):
    """
    Task to send an email notification when an order is successfully paid.
    """
    order = Order.objects.get(id=order_id)
    # create invoice e-mail
    subject = f'My Shop - Invoice no. {order.id}'
    message = (
        'Please, find the attached invoice for your recent purchase.'
    )
    email = EmailMessage(
        subject, message, 'admin@myshop.com', [order.email]
    )

    # generate PDF
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()     # Creates an in-memory buffer (like a virtual file in RAM).
    stylesheets = [weasyprint.CSS(finders.find('css/pdf.css'))]
    # WeasyPrint takes the rendered HTML + CSS and writes the raw binary PDF data into that buffer.
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    # Result: 'out' now holds the PDF content in bytes (not readable text)

    # attach a PDF file
    email.attach(
        f'order_{order.id}.pdf', out.getvalue(), 'application/pdf'
    )
    # out.getvalue() extracts the binary data from the memory buffer.
    # 'application/pdf' = MIME type, telling the receiver's email client/browser:
    # "This is a PDF, open with a PDF viewer".

    # send e-mail
    email.send()