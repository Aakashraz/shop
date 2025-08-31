import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from .models import Order, OrderItem
from django.utils.safestring import mark_safe
from django.urls import reverse

from import_export_celery.admin_actions import create_export_job_action
from import_export.admin import ImportExportModelAdmin
from .resources import OrderResource, MinimalOrderResource

print(f"OrderResource type: {type(OrderResource)}")


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


# def export_to_csv(modeladmin, request, queryset):
#     opts = modeladmin.model._meta
#     # Every Django model class has an internal attribute called _meta that holds metadata about the model—things like
#     # field definitions, verbose names, table names, etc.
#
#     # Building the Content-Disposition header string
#     content_disposition = (
#         f'attachment; filename={opts.verbose_name}.csv'
#     )
#     # Placing that header string into 'Content-Disposition' tells the browser two things:
#     # 'This response should be treated as a file attachment (i.e., prompt the user to download).'
#     # "When you save it, suggest the filename 'order.csv'".
#
#     response = HttpResponse(content_type='text/csv')
#     # This tells the browser, "Hey, the body of this response is CSV data."
#     response['Content-Disposition'] = content_disposition
#     # This line sets the Content-Disposition header on the HTTP response, ensuring that when the response is delivered,
#     # it will include the download instructions (with the correct filename) we created earlier.
#
#     writer = csv.writer(response)
#     # Here, a CSV writer object from Python's built-in csv module is created. This writer will output CSV-formatted
#     # data directly into the response object, which behaves like a file.
#
#     fields = [
#         field
#         for field in opts.get_fields()
#         if not field.many_to_many and not field.one_to_many
#     ]
#     # Above code in plain English: “I want a list of every model field that isn’t a reverse-relation or a pure
#     # many-to-many. Those are harder to represent in a flat CSV.”
#
#     # Write a first row with header information
#     writer.writerow([field.verbose_name for field in fields])
#
#     # Write down rows
#     # queryset is exactly the set of model instances the administrator checked before running the action.
#     # For example, if you checked three books and clicked “Export to CSV,” then
#     # queryset is a queryset containing those three Book objects.
#     for obj in queryset:
#         data_row = []
#         for field in fields:
#             value = getattr(obj, field.name)
#             if isinstance(value, datetime.datetime):
#                 value = value.strftime('%d/%m/%Y')  # convert the datetime field into str
#             data_row.append(value)
#         writer.writerow(data_row)
#     return response
# export_to_csv.short_description = 'Export to CSV'
# ------ Remove the custom export_to_csv function since the django-import-export library handles this. ------


def order_detail(obj):
    url = reverse('orders:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):   # admin.ModelAdmin changed to ImportExportModelAdmin to enable bulk import/export
    resource_class = OrderResource
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
        order_detail,

    ]
    list_filter = ['paid', 'created', 'updated']
    actions = [create_export_job_action]
    inlines = [OrderItemInline]


