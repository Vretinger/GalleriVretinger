from django import forms
from .models import EventBooking

class EventBookingForm(forms.ModelForm):
    class Meta:
        model = EventBooking
        fields = ['num_guests','name', 'email', 'phone']
        widgets = {
            'num_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10', 'value': '1'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Phone (optional)'}),
        }
