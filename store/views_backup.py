from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, OrderItem, OrderTransaction
from category.models import Category
from cart.models import Cart, CartItem
from cart.views import _cart_id
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import random
import string
from django.utils.timezone import now
from cart.views import merge_cart 

def store(request, category_slug=None):
    products = Product.objects.filter(is_available=True).order_by('id')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Handle the search query
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(product_name__icontains=query) | Q(description__icontains=query)
        )

    # Filter by size (fix: using variations)
    selected_sizes = request.GET.getlist('size')
    if selected_sizes:
        products = products.filter(variations__variation_category='Size', variations__variation_value__in=selected_sizes)

    # Filter by price range (fix: convert to float)
    try:
        min_price = float(request.GET.get('min_price', 0))
        max_price = float(request.GET.get('max_price', 999999))
    except ValueError:
        min_price, max_price = 0, 999999

    products = products.filter(price__gte=min_price, price__lte=max_price)

    # Define available sizes
    available_sizes = ["M", "L", "XL", "XXL"]

    # Pagination
    paginator = Paginator(products, 6)  # Show 6 products per page
    page_number = request.GET.get('page')
    paged_products = paginator.get_page(page_number)

    context = {
        'prod': paged_products,
        'p_count': products.count(),
        'query': query,
        'selected_sizes': selected_sizes,
        'min_price': min_price,
        'max_price': max_price,
        'available_sizes': available_sizes,
    }
    return render(request, 'store/store.html', context)






def product_details(request, category_slug, product_slug):
    category = get_object_or_404(Category, slug=category_slug)  # Fetch the category
    product = get_object_or_404(Product, slug=product_slug, category=category)  # Fetch the product
    in_cart = False
    if request.user.is_authenticated:
        in_cart = CartItem.objects.filter(product=product, user=request.user).exists()
    else:
        cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
        if cart:
            in_cart = CartItem.objects.filter(product=product, cart=cart).exists()

    context = {
        'prod': product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product_details.html', context)


@login_required
def dashboard(request):
    """Dashboard - Displays all orders for logged-in users with pagination and filtering."""
    status = request.GET.get('status')  # Filter orders by status (optional)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    if status:
        orders = orders.filter(status=status)  # Apply filtering

    paginator = Paginator(orders, 5)  # Show 5 orders per page
    page_number = request.GET.get('page')
    paged_orders = paginator.get_page(page_number)


    context = {
        'orders': paged_orders,
        'status': status,
    }
    return render(request, 'store/dashboard.html', context)

@login_required
def order_detail(request, order_id):
    """Order Detail - Shows a specific order and its items."""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'store/order_detail.html', context)


@login_required(login_url='login')
def checkout(request):
    """Handles checkout process and merges guest cart items with user cart."""
    
    # 🔹 Merge guest cart with logged-in user's cart
    merge_cart(request, request.user)

    # 🔹 Fetch cart items after merging
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('store')

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        shipping_address = request.POST.get('shipping_address')
        phone_number = request.POST.get('phone_number')
        payment_method = request.POST.get('payment_method')

        if not shipping_address or not phone_number:
            messages.error(request, "Please provide both shipping address and phone number.")
            return redirect('checkout')

        # 🔹 Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_price,
            shipping_address=shipping_address,
            phone_number=phone_number,
            status='pending',
            order_id=f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{request.user.id}",
        )

        # 🔹 Move cart items to order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
            )
        
        # 🔹 Clear cart after order placement
        cart_items.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_detail', order_id=order.order_id)

    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total_price': total_price})




def generate_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

@login_required(login_url='login')
def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        phone_number = request.POST.get('phone_number')
        payment_method = request.POST.get('payment_method')

        order = Order.objects.create(
            user=current_user,
            order_id=generate_order_id(),
            total_amount=total_price,
            shipping_address=shipping_address,
            billing_address=shipping_address,  # Assuming billing address is same as shipping
            phone_number=phone_number,
            status="pending",
        )

        for item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,
                variation=item.variations.first() if item.variations.exists() else None,
                quantity=item.quantity,
                price=item.product.price
            )

        # Create transaction record
        transaction = OrderTransaction.objects.create(
            order=order,
            transaction_id=f"TXN{random.randint(100000, 999999)}",
            amount=total_price,
            payment_method=payment_method,
            status="Pending" if payment_method == "Credit Card" else "Completed",
        )

        # Clear cart after order placement
        cart_items.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_success', order_id=order.order_id)

    return redirect('checkout')

@login_required(login_url='login')
def order_success(request, order_id):
    order = Order.objects.get(order_id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})