from django.db import models
from django.utils.text import slugify
from category.models import Category
from django.conf import settings
from django.db.models import Avg, Count

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
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count


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






class ReviewRating(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.FloatField()
    review = models.TextField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'




