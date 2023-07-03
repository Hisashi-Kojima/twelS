from django.contrib.auth.backends import ModelBackend
from .models import EmailUser


class PasswordlessAuthBackend(ModelBackend):
    """Log EmailUser in to Django without providing a password.
    """
    def authenticate(self, email=None):
        try:
            return EmailUser.objects.get(email=email)
        except EmailUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return EmailUser.objects.get(pk=user_id)
        except EmailUser.DoesNotExist:
            return None
