from django.contrib import admin
from .models import Booking, Coupon

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'purpose', 'is_confirmed', 'created_at')
    list_filter = ('is_confirmed', 'start_date')
    ordering = ('start_date', 'end_date')
    list_editable = ('is_confirmed',)
    search_fields = ('user__username', 'purpose')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "active", "valid_from", "valid_until")
    list_filter = ("active", "discount_type")
    search_fields = ("code",)