from django.db import models
from django.conf import settings
from django.utils import timezone

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    initial_payment_done = models.BooleanField(default=False)
    final_payment_due_date = models.DateField(null=True, blank=True)
    final_payment_done = models.BooleanField(default=False)
    initial_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_code = models.CharField(max_length=50, null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()
    purpose = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.start_date} → {self.end_date}"


class Coupon(models.Model):
    CODE_TYPE_CHOICES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=CODE_TYPE_CHOICES, default="percentage")
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)  # Either % or SEK
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        if not self.active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True