import json
from django.db import models

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
    itemJson= models.CharField(max_length=5000,default="")
    order_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    phone_number = models.IntegerField(default=0)
    zip_code = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class OrderUpdate(models.Model):
    update_Id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default=0)
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateField(auto_now_add=True)   

    def __str__(self):
        return self.update_desc[0:7] + "..."
    
class CartProd(models.Model):

    itemJson = models.CharField(max_length=200,default="")

    def __str__(self):
        data = json.loads(self.itemJson)
        for key in data:
            name = data[key][2]

        return name
