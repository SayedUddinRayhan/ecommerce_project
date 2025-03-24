from django.shortcuts import render
from store.models import Product, ReviewRating
# Create your views here.
def home(request):
    products = Product.objects.all().filter(is_available=True)

    # Get the reviews
    reviews = None
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
    context = {
        'prod': products,
        'reviews': reviews,
    }
    return render(request, 'home.html', context)