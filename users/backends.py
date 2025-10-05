from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class CaseInsensitiveEmailBackend(ModelBackend):
    """
    Authenticate using case-insensitive email.
    Password remains case-sensitive.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            # Compare lowercase emails
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            return None

        # Check password (still case-sensitive)
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
