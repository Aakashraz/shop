from django.conf import settings
from django.db import models
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from coupons.models import Coupon


class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    # To reference stripe payments in orders
    stripe_id = models.CharField(max_length=250, blank=True)
    coupon = models.ForeignKey(
        Coupon, related_name='orders', null=True,blank=True, on_delete=models.SET_NULL
    )
    # The discount field is stored in the related Coupon object, but you can include it
    # in the Order model to preserve it if the coupon has been modified or deleted. You
    # set on_delete to models.SET_NULL so that if the coupon gets deleted, the 'coupon'
    # field is set to NULL, but the discount is preserved.
    discount = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Order {self.id}'


    def get_total_cost(self):
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount()


    def get_total_cost_before_discount(self):
        return sum(item.get_cost() for item in self.items.all())
    # the return statement is basically:
    # "Loop through all items in this order, calculate each item's cost, and
    # then add them up to get the total price."


    def get_discount(self):
        total_cost = self.get_total_cost_before_discount()
        if self.discount:
            return total_cost * (Decimal(self.discount) / Decimal(100))
        return Decimal(0)


    def get_stripe_url(self):
        if not self.stripe_id:
            # no payment associated
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            # Stripe path for test payments
            path = '/test/'
        else:
            # Stripe path real payments
            path = '/'

        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)

    # we use the string 'shop.Product' with the format app.Model, which is
    # another way to point to related models and also a good method to avoid circular imports.
    product = models.ForeignKey('shop.Product', related_name='order_items', on_delete=models.CASCADE)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.id}'

    def get_cost(self):
        return self.price * self.quantity