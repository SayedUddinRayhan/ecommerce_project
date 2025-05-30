from django.shortcuts import render, redirect, get_object_or_404
from order.models import Product, Variation
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages




def _cart_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_variation = []

    if request.method == 'POST':
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product, variation_category__iexact=key, variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    print("Selected Variations:", product_variation)  # Debugging print statement

    if request.user.is_authenticated:
        cart_item_qs = CartItem.objects.filter(product=product, user=request.user)
    else:
        cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))
        cart_item_qs = CartItem.objects.filter(product=product, cart=cart)

    existing_cart_item = None
    for cart_item in cart_item_qs:
        if list(cart_item.variations.all()) == product_variation:
            existing_cart_item = cart_item
            break

    if existing_cart_item:
        existing_cart_item.quantity += 1
        existing_cart_item.save()
    else:
        cart_item = CartItem.objects.create(
        product=product,
        quantity=1,
        user=request.user if request.user.is_authenticated else None,
        cart=cart if not request.user.is_authenticated else None  # Assign cart for guest users
        )

        cart_item.variations.set(product_variation)
        cart_item.save()

    messages.success(request, "Product added to cart successfully!")
    return redirect('cart')


def remove_cart(request, product_id, cart_item_id):

    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request):
    total = 0
    quantity = 0
    tax = 0
    grand_total = 0

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:
        cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
        cart_items = CartItem.objects.filter(cart=cart, is_active=True) if cart else []
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)  # Ensure logged-in user sees their items



    for cart_item in cart_items:
        print(f"Product: {cart_item.product}, Quantity: {cart_item.quantity}, Variations: {list(cart_item.variations.all())}")  # Print cart item details
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)


