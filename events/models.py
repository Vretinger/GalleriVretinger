from django.db import models
from booking.models import Booking

class Event(models.Model):
    LAYOUT_CHOICES = [
        ('layout1', 'Layout 1 - Image left, text right'),
        ('layout2', 'Layout 2 - Text over image'),
        ('layout3', 'Layout 3 - Image grid'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=100)
    artist_intro = models.TextField()
    artist_portrait = models.ImageField(upload_to='artists/')
    description = models.TextField()
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='layout1')
    image = models.ImageField(upload_to='events/')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_current_event = models.BooleanField(default=False)
    is_upcoming_event = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='event_gallery/')

    def __str__(self):
        return f"Image for {self.event.title}"
