from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment stages
    initial_payment_done = models.BooleanField(default=False)
    initial_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_payment_done = models.BooleanField(default=False)
    final_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_payment_due_date = models.DateField(null=True, blank=True)
    contract_signed = models.BooleanField(default=False)
    contract_signature = models.ImageField(upload_to='contracts/signatures/', null=True, blank=True)
    signed_contract_pdf = models.URLField(max_length=500, null=True, blank=True)

    
    # Stripe tracking
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)

    # Booking details
    discount_code = models.CharField(max_length=50, null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()
    purpose = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.start_date} → {self.end_date}"
    
    # ✅ Derived properties
    @property
    def is_upcoming(self):
        return self.start_date > timezone.now().date()

    @property
    def days_until_start(self):
        return (self.start_date - timezone.now().date()).days

    @property
    def payment_status(self):
        """Return a readable payment status"""
        if self.initial_payment_done and self.final_payment_done:
            return "paid"
        elif self.initial_payment_done:
            return "partial"
        return "unpaid"

    @property
    def remaining_balance(self):
        """Calculate remaining balance for clarity"""
        if self.final_payment_done:
            return 0
        if self.initial_payment_done and self.initial_payment_amount:
            return float(self.total_price) - float(self.initial_payment_amount)
        return float(self.total_price)

    def set_final_payment_due(self):
        """Automatically set due date if applicable"""
        if self.days_until_start > 14:
            self.final_payment_due_date = self.start_date - timedelta(days=14)
        else:
            self.final_payment_due_date = timezone.now().date()  # due immediately

    def requires_final_payment(self):
        """True if 50% paid, event upcoming, and final not yet done"""
        return (
            self.initial_payment_done
            and not self.final_payment_done
            and self.start_date > timezone.now().date()
        )


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