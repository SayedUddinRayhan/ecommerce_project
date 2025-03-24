from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, OrderTransaction
from cart.models import CartItem
from django.contrib import messages
import random
import string
from django.utils import timezone
from django.core.paginator import Paginator
from decimal import Decimal

def generate_order_id():
    """Generate a unique order ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

@login_required
def checkout(request):
    """Handles the checkout process."""
    cart_items = CartItem.objects.filter(user=request.user, is_active=True).prefetch_related('product', 'variations')

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('store')

    # Calculate total price for each cart item (product price * quantity)
    for cart_item in cart_items:
        cart_item.total_price = cart_item.product.price * cart_item.quantity

    # Calculate grand total (you can include other calculations like tax here)
    total_price = sum(item.total_price for item in cart_items)
    tax = (2 * total_price) / 100  # 2% tax
    grand_total = total_price + tax

    if request.method == "POST":
        shipping_address = request.POST.get('shipping_address')
        phone_number = request.POST.get('phone_number')
        payment_method = request.POST.get('payment_method')

        if not shipping_address or not phone_number:
            messages.error(request, "Please provide both shipping address and phone number.")
            return redirect('checkout')

        # Create order
        order = Order.objects.create(
            user=request.user,
            order_id=generate_order_id(),
            total_amount=grand_total,
            shipping_address=shipping_address,
            phone_number=phone_number,
            status='pending',
        )

        # Add order items, including variations
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
            )

            # Add variations to order item
            order_item.variations.set(cart_item.variations.all())

        # Clear the cart after order placement
        cart_items.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_success', order_id=order.order_id)

    return render(request, 'order/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'tax': tax,
        'grand_total': grand_total
    })




@login_required
def order_details(request, order_id):
    """Shows order details including variations and return status."""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order).prefetch_related('variations')

    # Calculate subtotal
    subtotal = sum(Decimal(item.price) * Decimal(item.quantity) for item in order_items)

    # Calculate tax (2%) - ensure it's a Decimal
    tax_amount = subtotal * Decimal(0.02)

    # Calculate grand total
    grand_total = subtotal + tax_amount



    context = {
        'order': order,
        'order_items': order_items,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'grand_total': grand_total,

    }

    return render(request, 'order/order_details.html', context)




@login_required
def place_order(request):
    """Handles placing an order with stock validation and variations."""
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    # Check if any product in the cart exceeds stock
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(
                request,
                f"Not enough stock for {item.product.product_name}. Available: {item.product.stock}, Requested: {item.quantity}"
            )
            return redirect('cart')

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        phone_number = request.POST.get('phone_number')
        payment_method = request.POST.get('payment_method')

        # Create order
        order = Order.objects.create(
            user=current_user,
            order_id=generate_order_id(),
            total_amount=total_price,
            shipping_address=shipping_address,
            phone_number=phone_number,
            status="pending",
        )

        # Save order items with variations and update stock
        for item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            # Set variations to the order item
            order_item.variations.set(item.variations.all())

            # Reduce stock
            item.product.stock -= item.quantity
            item.product.save()

        # Create transaction record
        transaction = OrderTransaction.objects.create(
            order=order,
            transaction_id=f"TXN{random.randint(100000, 999999)}",
            amount=total_price,
            payment_method=payment_method,
            status="Pending" if payment_method == "Credit Card" else "Completed",
        )

        # Clear cart
        cart_items.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_success', order_id=order.order_id)

    return redirect('checkout')




from decimal import Decimal

@login_required
def order_success(request, order_id):
    """Renders the order success page with invoice details."""
    order = Order.objects.get(order_id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    # Calculate subtotal
    subtotal = sum(Decimal(item.price) * Decimal(item.quantity) for item in order_items)

    # Calculate tax (2%) - ensure it's a Decimal
    tax_amount = subtotal * Decimal(0.02)

    # Calculate grand total
    grand_total = subtotal + tax_amount

    context = {
        'order': order,
        'order_items': order_items,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'grand_total': grand_total,
    }

    return render(request, 'order/order_success.html', context)


@login_required
def orders(request):
    # Fetch all orders for the logged-in user
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Get status filter from request
    status_filter = request.GET.get("status", "")

    # Apply filtering if status is selected
    if status_filter:
        user_orders = user_orders.filter(status=status_filter)

    # Pagination
    paginator = Paginator(user_orders, 5)  # Show 5 orders per page
    page_number = request.GET.get("page")
    paged_orders = paginator.get_page(page_number)

    # Calculate tax and grand total safely
    for order in paged_orders:
        order.tax_amount = (order.total_amount or 0) * Decimal(0.02)
        order.grand_total = (order.total_amount or 0) + order.tax_amount

    context = {
        'orders': paged_orders,
        'status': status_filter,  # Pass status filter to the template
    }

    return render(request, 'order/orders.html', context)