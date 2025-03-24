from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),  # This is for all products (no category slug)
    path('category/<slug:category_slug>/', views.store, name='category_products'),  # This is for category filtering
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_details, name='product_details'),  # This is for product details
    path('dashboard/', views.dashboard, name='dashboard'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
    path('like_review/<int:review_id>/', views.like_review, name='like_review'),
    path('dislike_review/<int:review_id>/', views.dislike_review, name='dislike_review'),
]
