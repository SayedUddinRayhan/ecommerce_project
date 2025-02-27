from .models import Cart, CartItem
from .views import _cart_id

def cart_counter(request):
    cart_count = 0
    cart_items = []

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        # If the user has no cart items, check for session-based cart and merge
        if not cart_items.exists():
            cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
            if cart:
                guest_cart_items = CartItem.objects.filter(cart=cart)
                if guest_cart_items.exists():
                    cart_items = CartItem.objects.filter(user=request.user)
    else:
        cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
        if cart:
            cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        cart_count += item.quantity

    return {'cart_count': cart_count}