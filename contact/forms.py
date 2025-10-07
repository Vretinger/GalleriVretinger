from django import forms
from django.utils.translation import gettext_lazy as _

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label=_("Your Name"))
    email = forms.EmailField(label=_("Your Email"))
    message = forms.CharField(widget=forms.Textarea, label=_("Message"))
