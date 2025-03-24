from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
from cart.models import Cart, CartItem
from cart.views import _cart_id
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from order.models import Order, OrderItem
from django.contrib import messages
from django.http import JsonResponse
from .forms import ReviewForm
import json

def store(request, category_slug=None):
    # Fetch all categories
    categories = Category.objects.all()

    # Default products to all available ones
    products = Product.objects.filter(is_available=True).order_by('id')

    # If a category is selected, filter the products
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Handle the search query
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(product_name__icontains=query) | Q(description__icontains=query)
        )

    # Filter by size
    selected_sizes = request.GET.getlist('size')
    if selected_sizes:
        products = products.filter(variations__variation_category='Size', variations__variation_value__in=selected_sizes)

    # Filter by price range
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
        'categories': categories,  # Pass categories to the template
        'category_slug': category_slug,  # Pass the selected category slug to the template
        'p_count': products.count(),
        'query': query,
        'selected_sizes': selected_sizes,
        'min_price': min_price,
        'max_price': max_price,
        'available_sizes': available_sizes,
    }

    return render(request, 'store/store.html', context)







def product_details(request, category_slug, product_slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, slug=product_slug, category=category)

    in_cart = False
    if request.user.is_authenticated:
        in_cart = CartItem.objects.filter(product=product, user=request.user).exists()
        has_purchased = OrderItem.objects.filter(order__user=request.user, product=product).exists()
    else:
        cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
        if cart:
            in_cart = CartItem.objects.filter(product=product, cart=cart).exists()
        has_purchased = False


    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=product.id)

    context = {
        'prod': product,
        'in_cart': in_cart,
        'reviews': reviews,
        'has_purchased': has_purchased,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_details.html', context)



@login_required
def dashboard(request):
    """User Dashboard - Displays summary and recent orders"""
    user = request.user
    orders = Order.objects.filter(user=user).order_by("-created_at")

    total_orders = orders.count()
    total_spent = sum(order.total_amount for order in orders)

    # Order status breakdown for visualization
    order_status_counts = orders.values('status').annotate(count=Count('status'))
    order_status_data = {entry['status']: entry['count'] for entry in order_status_counts}


    context = {
        "user": user,
        "total_orders": total_orders,
        "total_spent": total_spent,
        "order_status_data": json.dumps(order_status_data),
    }
    return render(request, "store/dashboard.html", context)



def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER', 'store')

    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user=request.user, product_id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)

        if form.is_valid():
            data = form.save(commit=False)
            data.product_id = product_id
            data.user = request.user
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            messages.success(request, 'Thank you! Your review has been submitted.')
        else:
            messages.error(request, 'There was an error in your review submission.')

        return redirect(url)


@login_required
def like_review(request, review_id):
    review = get_object_or_404(ReviewRating, id=review_id)
    review.likes += 1
    review.save()
    return JsonResponse({'likes': review.likes})

@login_required
def dislike_review(request, review_id):
    review = get_object_or_404(ReviewRating, id=review_id)
    review.dislikes += 1
    review.save()
    return JsonResponse({'dislikes': review.dislikes})