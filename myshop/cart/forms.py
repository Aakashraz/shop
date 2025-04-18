from django import forms


PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1,21)]

class CartAddProductForm(forms.Form):
    # Each choice in a Django ChoiceField (or TypedChoiceField) is a tuple:
    # (actual_value, human_readable_label)
    # Even though HTML sends strings, the first value in the tuple must match the data type you expect after coercion.
    # That’s why (1, '1') is correct when using coerce=int.

    # The HTML uses the same first element of the tuple (2) as the value in the <option>, but sends it as
    # a string ('2'). Then Django converts that string back into an integer (2) using coerce=int, and
    # finally compares it to the same first element (2) in the choices.
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int,     # ensures quantity is an integer
    )
    override = forms.BooleanField(
        required=False,     # can be omitted in POST
        initial=False,      # defaults to False if not set
        widget=forms.HiddenInput,   # makes it a hidden field
    )