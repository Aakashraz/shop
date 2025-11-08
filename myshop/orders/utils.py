from decimal import Decimal


def calculate_shipping(weight: int) -> Decimal:
    if weight == 0:
        return Decimal('0.00')
    elif weight <= 1000:   # <= 1KG
        return Decimal('1.00')
    elif weight <= 2500:
        return Decimal('2.00')
    else:
        return Decimal('3.00') + Decimal((weight - 2500)/1000) * Decimal('1.00')