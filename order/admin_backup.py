from django.contrib import admin
from .models import Order, OrderItem, OrderTransaction

# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'total_amount', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'user__username')
    list_editable = ('status',)  # Allows status updates directly in the list view
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_as_processing.short_description = "Mark selected orders as Processing"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Mark selected orders as Delivered"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"

    def cancel_order(self, request, queryset):
        """Cancel orders that are still in 'pending' status."""
        for order in queryset:
            if order.status == 'pending':
                order.status = 'cancelled'
                order.save()
                self.message_user(request, f"Order {order.order_id} has been cancelled.")
            else:
                self.message_user(request, f"Order {order.order_id} cannot be cancelled because it is {order.status}.")

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'display_variations', 'quantity', 'price', 'total_price', 'return_status')
    list_filter = ('order', 'product', 'return_status')  # Add return_status to filter options
    search_fields = ('order__order_id', 'product__product_name')

    actions = ['approve_return', 'reject_return']

    def display_variations(self, obj):
        """Display variations of an order item."""
        return ', '.join([f"{variation.variation_category}: {variation.variation_value}" for variation in obj.variations.all()]) if obj.variations.exists() else "N/A"
    display_variations.short_description = 'Variation'

    def total_price(self, obj):
        """Calculate the total price for the order item."""
        return obj.quantity * obj.price
    total_price.short_description = 'Total Price'

    def approve_return(self, request, queryset):
        """Approve the return and increase the product stock."""
        for item in queryset:
            if item.return_status == 'requested':  # Ensure the return has been requested
                item.return_status = 'approved'
                item.product.stock += item.quantity  # Increase the stock
                item.product.save()
                item.save()
                self.message_user(request, f"Return for Order Item {item.id} has been approved.")
            else:
                self.message_user(request, f"Return for Order Item {item.id} cannot be approved.")

    approve_return.short_description = "Approve Return"

    def reject_return(self, request, queryset):
        """Reject the return."""
        for item in queryset:
            if item.return_status == 'requested':  # Only allow rejection for 'requested' status
                item.return_status = 'rejected'
                item.save()
                self.message_user(request, f"Return for Order Item {item.id} has been rejected.")
            else:
                self.message_user(request, f"Return for Order Item {item.id} cannot be rejected.")

    reject_return.short_description = "Reject Return"  

@admin.register(OrderTransaction)
class OrderTransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'transaction_id', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('transaction_id', 'order__order_id')

    def save_model(self, request, obj, form, change):
        """Automatically update the order status based on transaction status."""
        super().save_model(request, obj, form, change)

        # Check if transaction status is completed
        if obj.status.lower() == 'completed':  # Adjust based on actual transaction statuses
            obj.order.status = 'processing'  # Update order status when payment is successful

        # If the transaction is refunded, update order status to refunded
        elif obj.status.lower() == 'refunded':  
            obj.order.status = 'refunded'  # Mark the order as refunded
            self._update_product_stock_on_refund(obj.order)  # Handle product stock changes on refund

        # If the transaction failed or was canceled, mark the order as canceled
        elif obj.status.lower() in ['failed', 'cancelled']:
            obj.order.status = 'cancelled'

        obj.order.save()


    def _update_product_stock_on_refund(self, order):
        """Increase the stock for products when the order is refunded."""
        for order_item in order.items.all():
            if order_item.return_status == 'approved':  # Only update stock for approved returns
                order_item.product.stock += order_item.quantity
                order_item.product.save()


