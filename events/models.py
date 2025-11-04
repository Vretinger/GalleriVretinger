from django.db import models
from booking.models import Booking
from cloudinary.models import CloudinaryField
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta
import os

class Event(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    short_description = models.TextField()
    Full_description = models.TextField()
    is_drop_in = models.BooleanField(default=True, help_text="If unchecked, visitors must sign up for the event.")
    max_attendees = models.PositiveIntegerField(null=True, blank=True, help_text="Only required for sign-up events.")

    is_upcoming_event = models.BooleanField(default=True)

    potrait_image = CloudinaryField("potrait_image")
    event_image = CloudinaryField("event_image", null=True, blank=True,)
    is_gallery_event = models.BooleanField(default=False)

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
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="images", null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = CloudinaryField ('image', folder='artworks/')
    price = models.PositiveIntegerField(null=True, blank=True)
    art_id = models.CharField(max_length=100)  # Unique identifier for the artwork

    def __str__(self):
        return f"Image for {self.event.title}"


class EventDay(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="days")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()


class EventBooking(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(
        max_length=15, blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{7,15}$',
                message="Enter a valid phone number (7–15 digits, optional +)."
            )
        ]
    )
    num_guests = models.PositiveIntegerField(default=1)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.event.title}"