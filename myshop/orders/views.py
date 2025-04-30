from django.shortcuts import render
from cart.cart import Cart
from .forms import OrderCreateForm
from .models import OrderItem


# Create your views here.

def order_create(request):
    # Retrieve the current cart from the session with cart = Cart(request).
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:   # this calls your __iter__ above from cart.py
                # each item looks like:
                # { 'product': <Product instance>,
                #   'price': Decimal('19.99'),
                #   'quantity': 2 }

                OrderItem.objects.create(
                    order=order,                # the Order instance you just saved
                    product=item['product'],    # a Product model instance
                    price=item['price'],        # price at time or order
                    quantity=item['quantity']   # how many units
                )
            # item['price'] and item['quantity'] came straight from your session data via the Cart’s __iter__.

            # clear the cart
            cart.clear()
            # You want to remove the old cart data so that:
            # The user sees an empty cart on their next visit.
            # They can’t accidentally re-submit the same items again.

            return render(
                request, 'orders/order/created.html', {'order':order}
            )
    else:
        form = OrderCreateForm()
    return render(
        request,
        'orders/order/create.html',
        {'cart':cart, 'form':form}
    )