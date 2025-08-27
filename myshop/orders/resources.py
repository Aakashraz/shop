from import_export import resources, fields
from import_export.widgets import DateTimeWidget, BooleanWidget

from .models import Order
import logging
import traceback


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
    # Define boolean field with proper widget
    paid = fields.Field(column_name='paid', attribute='paid',
                        widget=BooleanWidget()
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
            error_msg = f"Error in before_import_row at row {row_number}: {type(e).__name__}: {e}"
            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")
            print(error_msg)
            print(f"Row Data: {row}")
            raise


    def import_row(self, row, instance_loader, **kwargs):
        try:
            instance = instance_loader.get_instance(row)
            # Process each row (optional additional logging)
            if instance:
                logger.info(f"Updating order for email: {row.get('email', 'N/A')}")
            else:
                logger.info(f"Creating order for email: {row.get('email', 'N/A')}")

            return super().import_row(row, instance_loader, **kwargs)
        except Exception as e:
            error_msg = f"Error in import_row: {type(e).__name__}:{e}"
            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")
            print(error_msg)
            print(f"Row Data: {row}")
            raise


    def after_import_row(self, row, row_result, row_number=None, **kwargs):
        try:
            if row_result.errors:
                logger.error(f"Row {row_number} errors: {row_result.errors}")
                print(f"Row {row_number} errors: {row_result.errors}")
            return super().after_import_row(row, row_result, **kwargs)
        except Exception as e:
            error_msg = f"Error in after_import_row at row {row_number}: {type(e).__name__}: {e}"
            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")
            print(error_msg)
            raise



# Minimal version for testing
class MinimalOrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = ('email', 'first_name', 'last_name')
        import_id_fields = ('email',)
