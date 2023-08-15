from django.contrib import admin
from .models import Product ,Contact, Order, CartProd, Return, newAddress

admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Order)
admin.site.register(CartProd)
admin.site.register(newAddress)
admin.site.register(Return)
# Register your models here.
