from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Coupon(models.Model):
    code= models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    # MinValueValidator(0); The discount cannot be less than 0.
    # MaxValueValidator(100); The discount cannot be more than 100.
    # These validators run before Django saves the object to the database (and also when you run form validation).
    # If the value is outside the allowed range, Django will raise a ValidationError.
    discount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage value (0 to 100)'
    )
    active = models.BooleanField()

    def __str__(self):
        return self.code
