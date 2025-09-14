from decimal import Decimal
from django.conf import settings
from shop.models import Product
from coupons.models import Coupon



class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session  # Gets the session dict
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart
        # store current applied coupon
        self.coupon_id = self.session.get('coupon_id')

    # Example of self.cart:
    # self.cart = {
    #     '1': {'quantity': 2, 'price': '10.99'},  # Product ID 1
    #     '2': {'quantity': 1, 'price': '5.50'}    # Product ID 2
    # }


    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        • product: The product instance to add or update in the cart.
        • quantity: An optional integer with the product quantity. This defaults to 1.
        • override_quantity: A Boolean that indicates whether the quantity needs to be overridden
          with the given quantity (True) or whether the new quantity has to be added to the existing
          quantity (False).
        """
        # (Session keys are strings in Django)
        product_id = str(product.id)
        if product_id not in self.cart:         # First-time addition
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)     # Price locked here
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity    # Replace
        else:
            self.cart[product_id]['quantity'] += quantity   # Add/Update
        self.save()


    def save(self):
        # mark the session as "modified" to ensure persistence which makes sure it gets saved,
        # this tells Django that the session has changed and needs to be saved
        # Without this quantity changes might not save properly
        self.session.modified = True


    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()


    # This __iter__() method will allow you to easily iterate over
    # the items in the cart in views and templates.
    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        # Get all product IDs from the session cart
        product_ids = self.cart.keys()

        # get the product objects from a database and add them to the cart.
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()     # Avoid modifying the original cart

        # Inject full Product instances into cart items
        for product in products:
            cart[str(product.id)]['product'] = product
            # Now, example:  cart['42'] == {'price': '19.99', 'quantity': 2, 'product': <Product 42>}
            print(type(cart[str(product.id)]['product']))  # Output: <class 'shop.models.Product'>

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            # now item also still has 'product' and 'quantity' which was injected earlier in the add()
            yield item
            print(f'item from the __iter__ method: {item}')
            # Instead of returning a full list, this yields one cart item at a time
            # (makes the class memory efficient and iterable).
            # Each item yielded looks like:
            # {
            #     'quantity': 2,
            #     'price': Decimal('10.99'),
            #     'product': <Product object>,
            #     'total_price': Decimal('21.98')
            # }


    # custom __len__() method to return the total number of items stored in the cart.
    def __len__(self):
        """
        Count all items in the cart.
        """
        print(f'length of cart: {len(self.cart)} products')
        return sum(item['quantity'] for item in self.cart.values())


    # To calculate the total cost of the items in the cart
    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity'] for item in self.cart.values()
        )
    # A generator expression is a compact way to create an iterator — something you can loop over —
    # - without storing the entire list in memory.
    # syntax: (expression for item in iterable)


    # Method to clear the cart session
    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()


    # @property turns a method into something that looks and behaves like a normal attribute, but
    # still runs login when accessed. Here, it's used so you can treat coupon as a simple attribute
    # of the cart, even though it's actually doing a database fetch.
    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None


    def get_discount(self):
        if self.coupon:
            return (
                self.coupon.discount / Decimal(100)
            ) * self.get_total_price()
        return Decimal(0)


    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()