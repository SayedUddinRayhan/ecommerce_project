from .models import Cart, CartItem
from .views import _cart_id


def cart_counter(request):
    cart_count = 0
    cart_items = []  # Initialize an empty list
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
        if cart:
            cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        cart_count += item.quantity  # Count total quantity, not unique products
    
    return {'cart_count': cart_count}