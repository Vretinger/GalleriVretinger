import os
import django

# Set the settings module for your project
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
# Change these values as you want
EMAIL = "fruvretinger@hotmail.com"
FIRST_NAME = "Annika"
LAST_NAME = "Vretinger"
PASSWORD = "HampusIsak"

try:
    user = User.objects.get(email=EMAIL)
    if not user.is_superuser:
        user.is_superuser = True
        user.is_staff = True  # required to access admin
        user.set_password(PASSWORD)  # optional: update password
        user.save(update_fields=["is_superuser", "is_staff", "password"])
        print("Existing user upgraded to superuser!")
    else:
        print("User is already a superuser.")
except User.DoesNotExist:
    # Create a new superuser without 'username'
    User.objects.create_superuser(
        email=EMAIL,
        first_name=FIRST_NAME,
        last_name=LAST_NAME,
        password=PASSWORD
    )
    print("Superuser created successfully!")
