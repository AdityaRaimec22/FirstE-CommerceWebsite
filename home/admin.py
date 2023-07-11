from django.contrib import admin
from .models import Product ,Contact, Order, OrderUpdate, CartProd

admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Order)
admin.site.register(CartProd)
admin.site.register(OrderUpdate)
# Register your models here.
