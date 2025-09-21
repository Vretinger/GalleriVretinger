from django.urls import path
from . import views

urlpatterns = [
    path("availability/", views.availability_view, name="availability"),
    path("booked-dates/", views.booked_dates, name="booked_dates"),
    path("booking/", views.booking_page, name="booking_page"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
]
