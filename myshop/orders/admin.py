from django.contrib import admin
from .models import Order, OrderItem
from django.utils.safestring import mark_safe


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

# —It’s a standalone helper function. Django allows you to add a “callable” (a function or method)
# to list_display, which it will call for each row.
def order_payment(obj):
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        # The target="_blank" attribute causes it to open the Stripe page in a new tab.
        return mark_safe(html)
        # We wrap that string with mark_safe(…) because by default Django would escape <a href="…"> into literal &lt;a href="…"&gt;.
        # Instead, mark_safe tells Django, “I’ve constructed well-formed HTML—go ahead and render it.”
    return '-'
order_payment.short_description = 'Stripe payment'
# This line sets the column header in the admin list view as "Stripe payment" instead of
# "Order payment" or "order_payment" as the column title


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'first_name',
        'last_name',
        'email',
        'address',
        'postal_code',
        'city',
        'paid',
        order_payment,
        'created',
        'updated',
    ]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]


