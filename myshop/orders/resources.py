from import_export import resources
from .models import Order
import logging


logger = logging.getLogger(__name__)

class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = ('id', 'first_name', 'last_name', 'email', 'address', 'postal_code',
                  'city', 'paid', 'created', 'updated', 'stripe_id')
        export_order = ('id', 'first_name', 'last_name', 'email', 'address', 'postal_code',
                        'city', 'paid', 'created', 'updated', 'stripe_id')
        import_id_fields = ('email',)   # Optional unique identifier


        def before_import_row(self, row, row_number=None, **kwargs):
            logger.info(f"Processing row {row_number}: {row.get('email', 'N/A')}")
            # Alternatively, print directly for immediate output
            print(f"Processing row {row_number}: {row.get('email', 'N/A')}")


        def import_row(self, row, instance, **kwargs):
            # Process each row (optional additional logging)
            if instance:
                logger.info(f"Updating order for email: {row.get('email', 'N/A')}")
            else:
                logger.info(f"Creating order for email: {row.get('email', 'N/A')}")

            return super().import_row(row, instance, **kwargs)
