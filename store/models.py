from django.db import models
from django.utils.text import slugify
from category.models import Category
from django.conf import settings  # Import settings to reference the custom user model

# Create your models here.
class Product(models.Model):
    product_name    = models.CharField(max_length=255, unique=True)
    slug            = models.SlugField(max_length=255, unique=True, blank=True)
    description     = models.TextField(blank=True)
    price           = models.DecimalField(max_digits=10, decimal_places=2)
    image           = models.ImageField(upload_to='photos/products/', blank=True, null=True)
    stock           = models.PositiveIntegerField(default=0)
    is_available    = models.BooleanField(default=True)
    requires_size = models.BooleanField(default=False)
    requires_color = models.BooleanField(default=False)
    category        = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)  # Generate slug from product name
        super().save(*args, **kwargs)


    def __str__(self):
        return self.product_name
    

class VariationCategory(models.TextChoices):
    COLOR = 'Color', 'Color'
    SIZE = 'Size', 'Size'


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    variation_category = models.CharField(max_length=50, choices=VariationCategory.choices)
    variation_value = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'variation_category', 'variation_value')

    def __str__(self):
        return f"{self.product.product_name} - {self.variation_category}: {self.variation_value}"
    


class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')  # Use settings.AUTH_USER_MODEL here
    order_id = models.CharField(max_length=255, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    billing_address = models.TextField()
    phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    variation = models.ForeignKey(Variation, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} ({self.variation})"

    def total_price(self):
        return self.quantity * self.price


class OrderTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} for Order {self.order.order_id}"
