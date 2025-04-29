from django import forms
from .models import Order



class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
            'address',
            'postal_code',
            'city'

        ]
        # Validation (e.g., required fields, data types) comes from the model too.
        # If you ever change the model (e.g., make email optional), the form behavior updates accordingly.
