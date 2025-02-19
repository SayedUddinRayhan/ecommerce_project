from django.contrib import admin
from .models import Product


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'stock', 'created_at', 'is_available')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'category_name')
    prepopulated_fields = {'slug': ('product_name',)}
# Register your models here.
admin.site.register(Product, ProductAdmin)