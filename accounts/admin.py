from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name', 'username')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('date_joined',)

    filter_horizontal = ()
    list_filter = ('is_active', 'is_staff', 'is_superadmin')
    fieldsets = (
        ("Personal Info", {'fields': ('first_name', 'last_name', 'email', 'username', 'phone_number')}),
        ("Permissions", {'fields': ('is_admin', 'is_staff', 'is_active', 'is_superadmin')}),
        ("Important Dates", {'fields': ('last_login', 'date_joined')}),
    )

# Register only the User model
admin.site.register(CustomUser, AccountAdmin)