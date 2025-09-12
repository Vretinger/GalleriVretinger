from django import forms
from events.models import Event

class BookingEventForm(forms.Form):
    # Booking fields
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    purpose = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    # Event fields
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    layout = forms.ChoiceField(choices=Event.LAYOUT_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    image1 = forms.ImageField(required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
