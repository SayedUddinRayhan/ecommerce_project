from django.contrib import admin
from .models import Cart, CartItem

class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'user', 'get_user_email', 'date_added')  # Show Cart ID, User, Email, Date Added
    list_filter = ('user', 'date_added')
    search_fields = ('cart_id', 'user__username', 'user__email')

    def get_user_email(self, obj):
        return obj.user.email if obj.user else "Guest"
    get_user_email.short_description = 'Email'  # Change column name in admin panel


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'user', 'get_user_email', 'formatted_date_added')  # Fetch date safely
    list_filter = ('user', 'cart', 'date_added')
    search_fields = ('cart__cart_id', 'user__username', 'user__email', 'date_added')

    def get_user_email(self, obj):
        return obj.user.email if obj.user else "Guest"
    get_user_email.short_description = 'Email'

    def formatted_date_added(self, obj):
        return obj.date_added.strftime('%Y-%m-%d %H:%M:%S') if obj.date_added else "N/A"
    formatted_date_added.short_description = "Date Added"

    def get_search_results(self, request, queryset, search_term):
        """
        Override search functionality to support case-insensitive search.
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        # Add support for case-insensitive username and email search
        if search_term:
            queryset |= self.model.objects.filter(user__username__icontains=search_term)
            queryset |= self.model.objects.filter(user__email__icontains=search_term)

        return queryset, use_distinct


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
