from django.urls import path
from . import views

urlpatterns = [
    path('booking_details/', views.booking_with_event, name='booking_details'),
    path("calendar/", views.booking_date_selection, name="booking_date_selection"),
    path("calendar/booked-dates/", views.booked_dates, name="booked_dates"),
    path("calendar/save-dates/", views.save_selected_dates, name="save_selected_dates"),
    path("submit-final-booking/", views.final_booking_submit, name="final_booking_submit"),
]
