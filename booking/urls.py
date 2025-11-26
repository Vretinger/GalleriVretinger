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
    path("pay_remaining_balance/<int:booking_id>/", views.pay_remaining_balance, name="pay_remaining_balance"),
    path("contract/<int:booking_id>/", views.sign_contract, name="sign_contract"),
    path("contract/<int:booking_id>/save/", views.save_signature, name="save_signature"),
    path("cancel_unpaid_booking/<int:booking_id>/", views.cancel_unpaid_booking, name="cancel_unpaid_booking"),
    path("admin/discounts/add/", views.add_discount, name="add_discount"),
    path("admin/discounts/edit/<int:discount_id>/", views.edit_discount, name="edit_discount"),
    path("admin/discounts/delete/<int:discount_id>/", views.delete_discount, name="delete_discount"),
]
