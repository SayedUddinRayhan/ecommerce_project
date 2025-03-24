from django.contrib import admin
from .models import Product, Variation, ReviewRating, ProductGallery

import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'stock', 'created_at', 'is_available')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'category_name')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]

@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'is_active')
    search_fields = ('product__product_name', 'variation_value')


@admin.register(ReviewRating)
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'review', 'created_at', 'updated_at')
    list_filter = ('user', 'rating', 'created_at')
    search_fields = ('user__username', 'product__product_name')

admin.site.register(ProductGallery)