from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, send_mail
from .models import CustomUser, AdminLoginAttempt
from .tokens import account_activation_token
from django.contrib.auth.decorators import login_required
from cart.models import CartItem
from cart.views import _cart_id, Cart, CartItem
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from .forms import ProfileEditForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseForbidden


# Register (Sign Up)
def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use")
            return redirect("register")

        user = CustomUser.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            phone_number=phone_number,
            password=password
        )
        user.is_active = False
        user.save()

        # 🔹 Send activation email
        current_site = get_current_site(request)
        mail_subject = "Activate Your Account"
        message = render_to_string("accounts/activation_email.html", {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        })
        email_message = EmailMessage(mail_subject, message, to=[email])
        email_message.content_subtype = "html"
        email_message.send()

        messages.success(request, "Please check your email to activate your account.")
        return redirect("activation_pending")

    return render(request, "accounts/register.html")



def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Get guest cart before login
            guest_cart = Cart.objects.filter(cart_id=_cart_id(request)).first()

            # Log in the user
            login(request, user)

            # Transfer cart items after login
            if guest_cart:
                guest_cart_items = CartItem.objects.filter(cart=guest_cart)

                for guest_item in guest_cart_items:
                    existing_cart_item = CartItem.objects.filter(
                        user=user,
                        product=guest_item.product
                    )

                    match_found = None
                    for cart_item in existing_cart_item:
                        if list(cart_item.variations.all()) == list(guest_item.variations.all()):
                            match_found = cart_item
                            break

                    if match_found:
                        match_found.quantity += guest_item.quantity
                        match_found.save()
                        guest_item.delete()
                    else:
                        guest_item.user = user
                        guest_item.cart = None  # Unlink from guest session cart
                        guest_item.save()

                # Delete the guest cart
                guest_cart.delete()

              # 🔹 Check if the logged-in user has any cart items
            user_cart_items = CartItem.objects.filter(user=user).exists()
            if user_cart_items:
                return redirect("cart")
            else:
                return redirect("home")  # Redirect to home page if no cart items
        else:
            messages.error(request, "Invalid credentials")
            return redirect("login")

    return render(request, "accounts/login.html")




# Logout (Sign Out)
def user_logout(request):
    logout(request)  # Django's built-in logout function
    messages.success(request, "You have been logged out")
    return redirect("login")


# Account Activation
def activate_view(request, uidb64, token):
    try:
        # Decode the uid from the URL
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated! You can now log in.")
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link.")
        return redirect("register")


# Activation Pending Page
def activation_pending(request):
    return render(request, "accounts/activation_pending.html")


User = get_user_model()



# 🔹 Forgot Password - Send Reset Email

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(f'/accounts/reset-password/{uid}/{token}/')

            # Email content
            subject = "Reset Your Password"
            html_message = render_to_string('accounts/password_reset_email.html', {'reset_url': reset_url, 'user': user})

            # Send email as HTML
            email_message = EmailMultiAlternatives(
                subject=subject,
                body="Please use an HTML-compatible email client to view this message.",
                from_email='your-email@example.com',
                to=[email]
            )
            email_message.attach_alternative(html_message, "text/html")
            email_message.send()

            messages.success(request, "A password reset link has been sent to your email.")
            return redirect('login')
        else:
            messages.error(request, "Email address not found.")

    return render(request, 'accounts/forgot_password.html')


def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect('login')
            else:
                messages.error(request, "Passwords do not match.")

        return render(request, 'accounts/reset_password.html')
    else:
        messages.error(request, "The reset link is invalid or has expired.")
        return redirect('forgot_password')




@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('dashboard')
    else:
        form = ProfileEditForm(instance=user)

    return render(request, 'accounts/profile_edit.html', {'form': form})



@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()  # Save the new password
            update_session_auth_hash(request, form.user)  # Keep the user logged in after changing the password
            messages.success(request, "Your password has been updated successfully.")
            return redirect('dashboard')  # Redirect to the dashboard after success
        else:
            messages.error(request, "Please correct the errors below.")  # Show errors if form is invalid
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form': form})



def fake_admin_login(request):
    """Fake admin login honeypot to catch unauthorized attempts"""
    ip = get_client_ip(request)
    AdminLoginAttempt.objects.create(username="UNKNOWN", ip_address=ip, status="HONEYPOT")

    return HttpResponseForbidden("<h2>403 Forbidden</h2><p>You are not authorized to access this page.</p>")

def get_client_ip(request):
    """Extract client IP address from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip