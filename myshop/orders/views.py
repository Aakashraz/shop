from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render, get_object_or_404
from cart.cart import Cart
from .forms import OrderCreateForm
from .models import Order, OrderItem
from .tasks import order_created


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
                # item from the __iter__ method: {'quantity': 5, 'price': Decimal('50.00'),
                # 'product': <Product: Red Tea>, 'total_price': Decimal('250.00')}
                OrderItem.objects.create(
                    order=order,                # the Order instance you just saved
                    product=item['product'],    # a Product model instance
                    price=item['price'],        # price at time of order
                    quantity=item['quantity']   # how many units
                )
            # item['price'] and item['quantity'] came straight from your session data via the Cart’s __iter__.

            # clear the cart
            cart.clear()
            # You want to remove the old cart data so that:
            # The user sees an empty cart on their next visit.
            # They can’t accidentally re-submit the same items again.

            # launch an asynchronous task using celery
            order_created.delay(order.id)
            # set the order in the session
            request.session['order_id'] = order.id
            # redirect for payment
            return redirect('payment:process')

    else:
        form = OrderCreateForm()
    return render(
        request,
        'orders/order/create.html',
        {'cart':cart, 'form':form}
    )


# The staff_member_required decorator checks that both is_active and is_staff fields of
# the user requesting the page are set to True.
@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(
        request, 'admin/orders/order/detail.html', {'order': order}
    )

