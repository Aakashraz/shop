from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm
from .recommender import Recommender

# for switching language view
from django.shortcuts import redirect
from django.utils.translation import activate



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


# To switch language from 'es' to 'en' and vice versa.
def switch_language(request):
    # 1. Get the target language code('es', 'en', etc.,)
    lang_code = request.POST.get('language') or request.GET.get('language')
    # 2. Get where to redirect after switching (the current page path)
    next_url = request.POST.get('next') or request.GET.get('next', '/')
    # The above values are retrieved from - 'value' option in the 'input' tag in the base.html form with method 'post'

    # 3. If we got a language code, proceed
    if lang_code:
        # 4. Activate the new language for this request
        activate(lang_code)
        # Example: activate('es) makes Django operate in Spanish
        # 5. Store language choice in session (persists across requests)
        request.session['django_language'] = lang_code

        # 6. Try to extract product ID from the URL using regex
        import re
        match = re.match(r'^/[^/]+/(\d+)/', next_url)
        # Pattern breakdown: ^/[^/]+/(\d+)/
        # ^/ = start of string -- with the slash
        # [^/]+/ = one or more character but not slash char + slash (language code like 'es/')
        # (\d+) = capture digits (the product ID)
        # / = another slash
        # Example: '/es/4/green-tea/' -> matches, captures '4'

        # 7. If we found a product ID in the URL
        if match:
            product_id = match.group(1)     # Get the captured ID ('4')
            try:
                # 8 Fetch the product by ID
                product = Product.objects.get(id=product_id, available=True)

                # 9. CRITICAL: get_absolute_url() now runs with Spanish active!
                # Because we called activate('es') above, Django's translation
                # system now returns Spanish slug: 'te-verde' instead of 'green-tea'
                return redirect(product.get_absolute_url())
                # Returns: redirect('/es/4/te-verde/')
            except Product.DoesNotExist:
                pass    # Product not found.

    if next_url.startswith('/'):
        # Split URL: '/en/some/random/path/' -> ['', 'en', 'some' 'random/path/']
        parts = next_url.split('/', 3)  # Split using '/' with maximum of 4 results

        if len(parts) >= 3:
            # Replace old language with new: '/en/...' -> '/es/...'
            next_url = f'/{lang_code}/' + (parts[2] if len(parts) == 3 else parts[2] + '/' + parts[3])

    # 11. Redirect to the new URL
    response = redirect(next_url)
    # 12. Set language cookie (browser remembers language choice)
    response.set_cookie('django_language', lang_code)
    # Add a cookie to remember the language choice
    # Next time users visits, Django read this cookie and automatically uses that language

    return response

