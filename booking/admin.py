from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'purpose', 'approved', 'created_at')
    list_filter = ('approved', 'start_date')
    ordering = ('start_date', 'end_date')
    list_editable = ('approved',)
    search_fields = ('user__username', 'purpose')
