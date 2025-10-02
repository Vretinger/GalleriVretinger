from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "phone_number", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "first_name": "Enter your first name",
            "last_name": "Enter your last name",
            "email": "Enter your email",
            "phone_number": "Enter your phone number",
            "password1": "Enter password",
            "password2": "Confirm password",
        }
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control mb-3",
                "placeholder": placeholders.get(field_name, "")
            })
            # remove default help text
            field.help_text = None



class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "Enter your email",
            "password": "Enter your password",
        }
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control mb-3",
                "placeholder": placeholders.get(field_name, "")
            })
