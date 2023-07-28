from django.contrib import admin
from .models import Product ,Contact, Order, OrderUpdate, CartProd, Return

admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Order)
admin.site.register(CartProd)
admin.site.register(OrderUpdate)
admin.site.register(Return)
# Register your models here.
