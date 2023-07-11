from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.signin,name="signin"),
    path('signup',views.signup,name="signup"),
    path('home',views.home,name="home"),
    path('home/products/<int:myid>',views.products,name="products"),
    path('home/contact',views.contact,name="contact"),
    path('home/cart',views.cart,name="cart"),
    path('home/orders',views.orders,name="orders"),
    path('home/search',views.search,name="search"),
    path('home/cart/checkout',views.checkout,name="checkout"),
    # path('home/cart/productCheckout/<int:prodId>',views.productCheckout,name="productCheckout"),
    # path('home/deletJson',views.deleteJson,name="deleteJson"),
]