from datetime import timedelta
from booking.models import Coupon
from django.utils import timezone


def calculate_booking_price(start_date, end_date):
    """Calculate total SEK cost based on weekdays/weekends and discounts."""
    total = 0
    num_days = (end_date - start_date).days + 1
    days = []

    for i in range(num_days):
        day = start_date + timedelta(days=i)
        weekday = day.weekday()  # Monday=0, Sunday=6

        if weekday < 4:  # Mon–Thu
            total += 1500
        elif weekday == 4:  # Fri
            total += 1500
        elif weekday == 5:  # Sat
            total += 1500
        else:  # Sun
            total += 1500
        days.append(day)

    # --- Check for full weekend (Fri–Sun) ---
    if num_days == 3 and {d.weekday() for d in days} == {4, 5, 6}:
        total = 3000  # full weekend package

    # --- Check for full week (Mon–Sun) ---
    elif num_days == 7 and days[0].weekday() == 0:
        total = 4500

    # --- Long bookings ---
    elif num_days >= 10:
        total *= 0.9  # 10% discount

    return round(total)


def apply_discount_code(code: str, total_price: float):
    try:
        coupon = Coupon.objects.get(code__iexact=code)
        if not coupon.is_valid():
            return None
        if coupon.discount_type == "percentage":
            return total_price * (coupon.discount_value / 100)
        elif coupon.discount_type == "fixed":
            return float(coupon.discount_value)
    except Coupon.DoesNotExist:
        return None