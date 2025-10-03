from django.db import models
from booking.models import Booking
from cloudinary.models import CloudinaryField
from django.utils import timezone
from datetime import timedelta
import os

class Event(models.Model):
    """ LAYOUT_CHOICES = [
        ('layout1', 'Layout 1 - Image left, text right'),
        ('layout2', 'Layout 2 - Text over image'),
        ('layout3', 'Layout 3 - Image grid'),
    ] """

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    """layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='layout1')"""

    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)

    is_current_event = models.BooleanField(default=False)
    is_upcoming_event = models.BooleanField(default=True)

    bg_image = CloudinaryField("bg_image", blank=True, null=True)
    bg_color = models.CharField(max_length=7, default="#f5f5f5")
    blur_bg = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the event first

        # Recalculate current event logic after saving
        now = timezone.now()
        upcoming_events = Event.objects.filter(
            start_datetime__gte=now,
            start_datetime__lte=now + timedelta(days=7)
        ).order_by("start_datetime")

        # Reset all
        Event.objects.filter(is_current_event=True).update(is_current_event=False)

        # Mark the soonest one as current
        if upcoming_events.exists():
            first_event = upcoming_events.first()
            first_event.is_current_event = True
            super(Event, first_event).save()

    def __str__(self):
        return self.title

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="images")
    image = CloudinaryField("image")

    def __str__(self):
        return f"Image for {self.event.title}"


class EventDay(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="days")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
