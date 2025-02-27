from django.contrib import admin
from .models import Product, Variation
from .models import Order, OrderItem, OrderTransaction

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'stock', 'created_at', 'is_available')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'category_name')
    prepopulated_fields = {'slug': ('product_name',)}

@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'is_active')
    search_fields = ('product__product_name', 'variation_value')



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'user__username')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'variation', 'quantity', 'price', 'total_price')
    list_filter = ('order', 'product')
    search_fields = ('order__order_id', 'product__product_name')

@admin.register(OrderTransaction)
class OrderTransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'transaction_id', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('transaction_id', 'order__order_id')
