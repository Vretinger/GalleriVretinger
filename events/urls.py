from django.urls import path
from .views import event_list, calendar_view, event_detail

urlpatterns = [
    path('', event_list, name='event_list'),
    path('events/<int:event_id>/', event_detail, name='event_detail'),
    path('calendar/', calendar_view, name='calendar_view'),
]
