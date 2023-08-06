import json
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300)
    pub_date = models.DateField()
    image = models.ImageField(upload_to='home/images', default="")

    def __str__(self):
        return self.product_name


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    desc = models.CharField(max_length=500, default="")


    def __str__(self):
        return self.name
    
class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    itemJson= models.CharField(max_length=5000,default="")
    order_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    phone_number = models.IntegerField(default=0)
    zip_code = models.IntegerField(default=0)
    order_Update = models.CharField(max_length=200, default="")
    # current_Time = models.CharField(max_length=20,default="")
    Time = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.order_id)
    
    
class CartProd(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    itemJson = models.CharField(max_length=200,default="")

    def __str__(self):
        data = json.loads(self.itemJson)
        for key in data:
            name = data[key][2]

        return name
    
class Return(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, default="")
    phone = models.CharField(max_length=70,default="")
    email = models.CharField(max_length=100, default="")
    returnId = models.CharField(max_length=70, default="")
    desc = models.CharField(max_length=500, default="")

    def __str__(self):
        return self.returnId
    
class Address(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100,default="")
    primary = models.BooleanField(default=False)
    phone = models.CharField(max_length=10, default="")
    pincode = models.CharField(max_length=10, default="")
    city = models.CharField(max_length=200, default="")
    street = models.CharField(max_length=300, default="")
    state = models.CharField(max_length=50, default="")

    def __str__(self):
        return self.name

