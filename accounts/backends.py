from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """Authenticate using either username or email."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username:
            try:
                user = User.objects.get(email=username)  # Allow login with email
            except User.DoesNotExist:
                try:
                    user = User.objects.get(username=username)  # Allow login with username
                except User.DoesNotExist:
                    return None

            # ✅ Ensure `is_superuser` is not lost
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
