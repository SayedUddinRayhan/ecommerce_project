from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_details, name='product_details'),
    path('category/<slug:category_slug>/', views.store, name='category_products'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order/<str:order_id>/', views.order_detail, name='order_detail'),
    path('place_order/', views.place_order, name='place_order'),
    path('order_success/<str:order_id>/', views.order_success, name='order_success'),
    

]