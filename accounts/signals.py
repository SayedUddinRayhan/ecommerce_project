from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from .models import AdminLoginAttempt
from django.contrib.auth import get_user_model

User = get_user_model()

def get_client_ip(request):
    """Extract client IP address from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):
    """Save successful admin logins."""
    user = User.objects.get(pk=user.pk)  # Reload the user from the database

    if user.is_superadmin:
        ip = get_client_ip(request)
        AdminLoginAttempt.objects.create(username=user.username, ip_address=ip, status="SUCCESS")




@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Save failed login attempts."""
    ip = get_client_ip(request)
    username = credentials.get("username", "UNKNOWN")
    AdminLoginAttempt.objects.create(username=username, ip_address=ip, status="FAILED")
