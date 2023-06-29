from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from . models import Product, Contact, Order, OrderUpdate
from math import ceil
import json

def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username,password=pass1)

        if user is not None:
            login(request,user)
            fname = user.first_name
            messages.success(request,"you ae logged in successfully")
            # return render(request,"home.html",{'fname':fname})
            return redirect('home')

        else:
            messages.error(request,"Bad Credentials")
            return redirect('signin')


    return render(request, 'signin.html')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.save()

        messages.success(request, "Your account has been successfully created!! kindly logIn to continue. Thanks")

        return redirect('signin')

    return render(request, 'signup.html')

def home(request):
    allProds = []
    catProds = Product.objects.values('category','id')
    cats = {item['category'] for item in catProds}
    for cat in cats:
        prod = Product.objects.filter(category = cat)
        n = len(prod)
        nSlides = n//4 + ceil((n/4) - (n//4))
        allProds.append([prod,range(1,nSlides),nSlides])
    params = {'allprods':allProds}
    return render(request,'home.html',params)

def searchMatch(query , item):
    if query in item.product_name.lower() or query in item.desc.lower() or query in item.category.lower():
        return True
    else:
        return False
        
def search(request):
    query = request.GET.get('search')
    prods = []
    catProds = Product.objects.values('category','id')
    cats = {item['category'] for item in catProds}
    for cat in cats:
        prodTemp = Product.objects.filter(category = cat)
        prod = [item for item in prodTemp if searchMatch(query , item)]
        prods.append(prod)
    params = {'prods':prods}
    return render(request,'search.html',params)

def products(request,myid):

    product = Product.objects.filter(id=myid)
    return render(request,'products.html',{'product':product[0]})

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        desc = request.POST.get('desc','')
        contact = Contact(name=name,email=email,phone=phone,desc=desc)
        contact.save()
    return render(request,'contact.html')

def cart(request):
    cartProds = []
    catProds = Product.objects.values('category','id')
    cats = {item['category'] for item in catProds}
    for cat in cats:
        prod = Product.objects.filter(category = cat)
        cartProds.append([prod])
    params = {'cartProds':cartProds}
    return render(request,'cart.html',params)

def checkout(request):
    if request.method == "POST":
        itemJson = request.POST['itemJson']
        name = request.POST['name']
        email = request.POST['email']
        address = request.POST['address1'] + " " + request.POST['address2']
        city = request.POST['city']
        state = request.POST['state']
        phone_number = request.POST['phone_number']
        zip_code = request.POST['zip_code']

        userOrder = Order(itemJson=itemJson,name=name,email=email,address=address,city=city,state=state,phone_number=phone_number,zip_code=zip_code)

        userOrder.save()
        update = OrderUpdate(order_id = userOrder.order_id, update_desc = "The Order has been Placed.")
        update.save()
        thank = True
        id = userOrder.order_id
        return render(request,'checkout.html',{'thank':thank,'id':id})
    return render(request,'checkout.html')

def productCheckout(request,prodId):
    if request.method == "POST":
        itemJson = request.POST['itemJson']
        name = request.POST['name']
        email = request.POST['email']
        address = request.POST['address1'] + " " + request.POST['address2']
        city = request.POST['city']
        state = request.POST['state']
        phone_number = request.POST['phone_number']
        zip_code = request.POST['zip_code']

        soloOrder = Order(itemJson=itemJson,name=name,email=email,address=address,city=city,state=state,phone_number=phone_number,zip_code=zip_code)

        soloOrder.save()
        update = OrderUpdate(order_id = soloOrder.order_id, update_desc = "The Order has been Placed.")
        update.save()
        thank = True
        id = soloOrder.order_id
        return render(request,'productCheckout.html',{'thank':thank,'id':id})
    prodOrder1 = Product.objects.filter(id=prodId)

    return render(request,'productCheckout.html',{'prodOrder1':prodOrder1[0]})

def orders(request):
    orders = Order.objects.all()  # Fetch all orders
    orderUpd = OrderUpdate.objects.all()
    
    product_list = []
    for things in orderUpd:
        prodDesc = things.update_desc.strip()
        Time = things.timestamp

    for order in orders:
        item_json = order.itemJson.strip()
        if item_json:
            try:
                data = json.loads(item_json)
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {str(e)}")
                data = {}
        else:
            data = {}

        for key in data:
            product_key = tuple(data[key])
            imageSrc = product_key[2]
            description = product_key[3]
            price = product_key[4]
            name = product_key[1]
            quantity = product_key[0]
            product_list.append({'image_src': imageSrc, 'desc': description, 'price': price, 'name': name, 'qty': quantity,'prodDesc':prodDesc, 'Time':Time})

    return render(request, 'Orders.html', {'product_list': product_list})