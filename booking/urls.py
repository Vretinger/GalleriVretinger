from django.urls import path
from . import views

urlpatterns = [
    path("availability/", views.availability_view, name="availability"),
    path("booked-dates/", views.booked_dates, name="booked_dates"),
    path("booking/", views.booking_page, name="booking_page"),
    path("my_bookings/", views.my_bookings_view, name="my_bookings"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("payment-cancel/", views.payment_cancel, name="payment_cancel"),
    path('calculate_price/', views.calculate_price, name='calculate_price'),
    path('validate_coupon/', views.validate_coupon, name='validate_coupon'),
]
