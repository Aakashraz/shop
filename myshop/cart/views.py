from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from coupons.forms import CouponApplyForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        print(f'For Update/Add Value >>> quantity:{cd['quantity']}, override:{cd['override']}, price:{product.price}')
        print( f'Items(): {request.session.items()}, Expiry age: {request.session.get_expiry_date()}')
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)    # Loads current cart from session

    # For Debugging purpose
    for item in cart:
        print(f'item["product"].name: {item["product"].name}, item["quantity"]: {item["quantity"]}, '
              f'item["total_price"]: {item["total_price"]}')

    # update product quantities
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={
                # For dropdown, limit to 50 even if actual quantity is higher
                'quantity': min(item['quantity'],20),   # Pre-fill with current quantity
                'override': True                # Ensure replacement (not adding)
            }
        )
        # Store the actual quantity separately to display
        item['actual_quantity'] = item['quantity']

    coupon_apply_form = CouponApplyForm()
    return render(request, 'cart/detail.html',
                  {
                      'cart': cart,
                      'coupon_apply_form': coupon_apply_form,
                  }
                  )

