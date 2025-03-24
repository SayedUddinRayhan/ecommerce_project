from django.shortcuts import render
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate_view, name='activate'),  # Ensure this matches
    path("activation-pending/", lambda request: render(request, "accounts/activation_pending.html"), name="activation_pending"),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('change-password/', views.password_change, name='password_change'),
]
