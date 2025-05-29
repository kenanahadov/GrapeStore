from django.urls import path
from . import views
urlpatterns=[
    path('',views.home,name='home'),
    path('product/<int:pk>/',views.product_detail,name='product_detail'),
    path('add-cart/<int:pk>/',views.add_cart,name='add_cart'),
    path('remove-cart/<int:pk>/',views.remove_cart,name='remove_cart'),
    path('cart/',views.cart_view,name='cart'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('toggle-wishlist/<int:pk>/',views.toggle_wishlist,name='toggle_wishlist'),
    path('checkout/',views.checkout,name='checkout'),
    path('account/',views.account,name='account'),
    path('settings/',views.settings_view,name='settings'),
]
