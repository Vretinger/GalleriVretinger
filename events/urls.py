from django.urls import path
from .views import event_list, calendar_view, event_detail
from . import views

urlpatterns = [
    path('', event_list, name='event_list'),
    path('events/<int:event_id>/', event_detail, name='event_detail'),
    path('<int:event_id>/book/', views.book_event, name='book_event'),
    path('calendar/', calendar_view, name='calendar_view'),
    path("delete_uploaded_image/", views.delete_uploaded_image, name="delete_uploaded_image"),
]
