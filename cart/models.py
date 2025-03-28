from django.db import models
from store.models import Product, Variation
from accounts.models import CustomUser
from django.utils.timezone import now

# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True) 
    cart    = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    date_added = models.DateTimeField(default=now)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.product_name} - {', '.join([str(v) for v in self.variations.all()])}"
    
    def save(self, *args, **kwargs):
        if self.quantity > self.product.stock:
            raise ValueError(f"Cannot add {self.quantity} items. Only {self.product.stock} left in stock.")
        super().save(*args, **kwargs)
