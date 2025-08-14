from import_export import resources, fields
from import_export.widgets import DateTimeWidget

from .models import Order
import logging


logger = logging.getLogger(__name__)
logger.info("OrderResource module loaded!!!!!!!!!!!!!!!!!!!!!!!!")


class OrderResource(resources.ModelResource):
    # Define datetime fields with proper widget
    created = fields.Field(column_name='created', attribute='created',
                           widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
                           )
    updated = fields.Field(column_name='updated', attribute='updated',
                           widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
                           )

    class Meta:
        model = Order
        fields = ('id', 'first_name', 'last_name', 'email', 'address', 'postal_code',
                  'city', 'paid', 'created', 'updated', 'stripe_id')
        export_order = ('id', 'first_name', 'last_name', 'email', 'address', 'postal_code',
                        'city', 'paid', 'created', 'updated', 'stripe_id')
        import_id_fields = ('email',)   # Optional unique identifier


    def before_import_row(self, row, row_number=None, **kwargs):
        try:
            logger.info(f"Processing row {row_number}: {row.get('email', 'N/A')}")
            # Alternatively, print directly for immediate output
            print(f"Processing row {row_number}: {row.get('email', 'N/A')}")
            return super().before_import_row(row, **kwargs)
        except Exception as e:
            logger.error(f"Error in before_import_row: {e}")
            print(f"Error in before_import_row: {e}_")
            raise



    def import_row(self, row, instance_loader, **kwargs):
        instance = instance_loader.get_instance(row)
        # Process each row (optional additional logging)
        if instance:
            logger.info(f"Updating order for email: {row.get('email', 'N/A')}")
        else:
            logger.info(f"Creating order for email: {row.get('email', 'N/A')}")

        return super().import_row(row, instance_loader, **kwargs)
