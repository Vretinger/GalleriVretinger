# bookings/forms.py
from django import forms
from .models import Booking
from events.models import Event

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["start_date", "end_date", "purpose", "discount_code"]
        widgets = {
            "start_date": forms.HiddenInput(),
            "end_date": forms.HiddenInput(),
            "purpose": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "discount_code": forms.TextInput(attrs={"class": "form-control"}),
        }


class BookingEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "is_drop_in", "max_attendees", "portrait"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_drop_in": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "max_attendees": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "portrait": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }