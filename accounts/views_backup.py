from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .models import CustomUser
from store.models import Order
from .tokens import account_activation_token
from django.contrib.auth.decorators import login_required
from store.models import Product, Variation
from cart.models import CartItem
from cart.views import merge_cart
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


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



# Login (Sign In)
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")

            # Call the merge_cart function to transfer guest cart items to the logged-in user's cart
            merge_cart(request, user)  # Ensure this line exists

            return redirect("checkout")  # Redirect to checkout after login
        else:
            messages.error(request, "Invalid email or password")
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




@receiver(user_logged_in)
def merge_guest_cart(sender, request, user, **kwargs):
    merge_cart(request, user)
