from django.urls import path
from .views import booking_with_event

urlpatterns = [
    path('', booking_with_event, name='bookings'),
]
