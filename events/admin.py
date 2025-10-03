from django.contrib import admin
from .models import Event, EventImage

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'start_time', 'end_date', 'end_time', 'is_current_event')
    list_filter = ('is_current_event',)

    def start_date(self, obj):
        if obj.start_datetime:
            return obj.start_datetime.date()
        return "-"
    start_date.admin_order_field = 'start_datetime'
    start_date.short_description = 'Start Date'

    def start_time(self, obj):
        if obj.start_datetime:
            return obj.start_datetime.time()
        return "-"
    start_time.admin_order_field = 'start_datetime'
    start_time.short_description = 'Start Time'

    def end_date(self, obj):
        if obj.end_datetime:
            return obj.end_datetime.date()
        return "-"
    end_date.admin_order_field = 'end_datetime'
    end_date.short_description = 'End Date'

    def end_time(self, obj):
        if obj.end_datetime:
            return obj.end_datetime.time()
        return "-"
    end_time.admin_order_field = 'end_datetime'
    end_time.short_description = 'End Time'


@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ('event', 'image')
