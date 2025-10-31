from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm
from .recommender import Recommender



# It handles:
# Showing all products if no category is selected.
# Showing products in a specific category if one is selected via the URL (using the slug).
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        language = request.LANGUAGE_CODE
        # The 'translations' used inside here is from the category model's field.
        # When you query, You're saying: "Find a 'Category' where its related translations table
        # has a row with this language_code and slug".
        category = get_object_or_404(
            Category,   # <- Main table
            translations__language_code=language,   # <- Query the translations table
            translations__slug=category_slug        # <- Query the translations table
        )
        products = products.filter(category=category)

    return render(
        request,
        'shop/product/list.html',
        {
            'category': category,
            'categories': categories,
            'products': products,
        }
    )


def product_detail(request, id, slug):
    language = request.LANGUAGE_CODE
    product = get_object_or_404(
        Product,
        id=id,
        translations__language_code=language,
        translations__slug=slug,
        available=True
    )
    cart_product_form = CartAddProductForm()
    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)
    return render(
        request,
        'shop/product/detail.html',
        {
         'product':product,
         'cart_product_form':cart_product_form,
         'recommended_products': recommended_products
         }
    )
