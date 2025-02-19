from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from cart.models import Cart, CartItem
from cart.views import _cart_id
from django.core.paginator import Paginator
from django.db.models import Q

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
