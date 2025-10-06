import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from .tasks import payment_completed
from shop.models import Product
from shop.recommender import Recommender



# This(csrf_exempt) -  decorator tells Django to make an exception and allow this request to come through.
@csrf_exempt
def stripe_webhook(request):
    payload = request.body  # payload - The raw data sent by Stripe.
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']  # A unique digital signature that Stripe creates using
    # the payload and a secret key (STRIPE_WEBHOOK_SECRET) that only you and Stripe know.
    event = None

    try:
        # The stripe.Webhook.construct_event() method is a helper provided by Stripe's SDK,
        # designed to simplify the process of verifying webhook requests. This function performs
        # a "secret handshake". It recalculates the signature using the same secret key. If its
        # calculated signature matches the one Stripe sent in the header, the request is verified as authentic.
        #
        # To verify the event's signature header. If the event's payload or the signature is invalid,
        # we return an HTTP 400 Bad response. Otherwise, we return an HTTP 200 OK response.
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid Signature
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':  # Checks if this is the event for a completed checkout.
        session = event.data.object
        if (
            session.mode == 'payment'
            and session.payment_status == 'paid'
        ):
            try:
                order = Order.objects.get(
                    id=session.client_reference_id
                )
            except Order.DoesNotExist:
                return HttpResponse(status=404)
            # mark order as paid
            order.paid = True
            # store Stripe payment ID
            order.stripe_id = session.payment_intent
            order.save()

            # save item bought for product recommendations
            # when a new order payment is confirmed; you retrieve the Product objects associated with the order items.
            # Then, you create an instance of the Recommender class and call the products_bought() method to store
            # the products bought together in Redis.
            product_ids = order.items.values_list('product_id')
            products = Product.objects.filter(id__in=product_ids)
            r = Recommender()
            r.products_bought(products)

            # launch an asynchronous task
            payment_completed.delay(order.id)

    return HttpResponse(status=200) # If Stripe doesn't receive this 200 response, it will assume
    # the delivery failed and will try to send the same event again, which could lead to duplicate actions.
