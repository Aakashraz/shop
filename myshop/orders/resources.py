from import_export import resources
from .models import Order


class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = ('id', 'first_name', 'last_name', 'email', 'address', 'postal_code',
                  'city', 'paid', 'created', 'updated', 'stripe_id')
        export_order = ('id', 'first_name', 'last_name', 'email', 'address', 'postal_code',
                        'city', 'paid', 'created', 'updated')
