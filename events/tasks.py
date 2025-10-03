# events/tasks.py
from django.utils import timezone
from datetime import timedelta
from .models import Event

def update_current_event():
    now = timezone.now()

    # Reset all
    Event.objects.filter(is_current_event=True).update(is_current_event=False)

    # Get first upcoming event within 7 days
    upcoming = Event.objects.filter(
        start_datetime__gte=now,
        start_datetime__lte=now + timedelta(days=7)
    ).order_by("start_datetime").first()

    if upcoming:
        upcoming.is_current_event = True
        upcoming.save(update_fields=["is_current_event"])
