from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('order/<str:order_id>/', views.order_details, name='order_details'),
    path('place_order/', views.place_order, name='place_order'),
    path('order/success/<str:order_id>/', views.order_success, name='order_success'),
    path('orders/', views.orders, name='orders'),

]