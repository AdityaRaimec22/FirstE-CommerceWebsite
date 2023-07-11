from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from . models import Product, Contact, Order, OrderUpdate, CartProd
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
        allProds.append([prod, range(1,nSlides), nSlides])

    prodList = []
    items_In_cartProd = CartProd.objects.all()
    for item in items_In_cartProd:
        itemJson = item.itemJson.strip()

        if itemJson:
            data = json.loads(itemJson)

        else:
            data = {}

        for key in data:
            prodId = key
            prodList.append({"prodId":prodId}) 

    return render(request,'home.html',{'prodList':json.dumps(prodList),'allprods':allProds})

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

    prodList = []
    items_In_cartProd = CartProd.objects.all()
    for item in items_In_cartProd:
        itemJson = item.itemJson.strip()

        if itemJson:
            data = json.loads(itemJson)

        else:
            data = {}

        for key in data:
            prodId = key
            prodList.append({"prodId":prodId})
            
    params = {'prods':prods,'prodList':json.dumps(prodList)}

    return render(request,'search.html',params)

def products(request,myid):

    product = Product.objects.filter(id=myid)
    prodList = []
    items_In_cartProd = CartProd.objects.all()
    for item in items_In_cartProd:
        itemJson = item.itemJson.strip()

        if itemJson:
            data = json.loads(itemJson)

        else:
            data = {}

        for key in data:
            prodId = key
            prodList.append({"prodId":prodId})
    return render(request,'products.html',{'product':product[0], 'prodList':json.dumps(prodList)})

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        desc = request.POST.get('desc','')
        contact = Contact(name=name,email=email,phone=phone,desc=desc)
        contact.save()

    prodList = []
    items_In_cartProd = CartProd.objects.all()
    for item in items_In_cartProd:
        itemJson = item.itemJson.strip()

        if itemJson:
            data = json.loads(itemJson)

        else:
            data = {}

        for key in data:
            prodId = key
            prodList.append({"prodId":prodId})
    return render(request,'contact.html',{'prodList':json.dumps(prodList)})

def checkout(request):

    cart_product_list = []
    new_cart_product_list = []
    bool_storer = []
    idstr = ''
    if request.method == "POST":

        data = request.POST.get('requestBody')
        idstr = request.POST.get('idstr')
        prodCart = CartProd.objects.all()
        if data == '1':

            request.session['bool_storer'] = bool_storer
            bool_storer.append(True)
            bool_storer.append(False)
            

            if len(prodCart) != 0:

                request.session['cart_product_list'] = cart_product_list  

                for existing_prods in prodCart:

                    item_json = existing_prods.itemJson.strip()

                    if item_json:
                        try:
                            data = json.loads(item_json)
                        except json.JSONDecodeError as e:
                            data = {}
                    else:
                        data = {}

                    for key in data:
                        prodId = key
                        product_key = tuple(data[key])
                        imageSrc = product_key[1]
                        description = product_key[4]
                        price = product_key[3]
                        name = product_key[2]
                        quantity = product_key[0]
                        cart_product_list.append({'image_src': imageSrc, 'desc': description, 'price': price, 'name': name, 'qty': quantity,'prodId':prodId})

        elif data == '2':

            request.session['bool_storer'] = bool_storer
            bool_storer.append(False)
            bool_storer.append(True)

            request.session['new_cart_product_list'] = new_cart_product_list

            for existing_prods in prodCart:

                    item_json = existing_prods.itemJson.strip()

                    if item_json:
                        try:
                            data = json.loads(item_json)
                        except json.JSONDecodeError as e:
                            data = {}
                    else:
                        data = {}

                    for key in data:
                        # prodId = key
                        if key == idstr:
                            product_Id = key
                            product_key = tuple(data[key])
                            imageSrc = product_key[1]
                            description = product_key[4]
                            price = product_key[3]
                            name = product_key[2]
                            quantity = product_key[0]
                            new_cart_product_list.append({'image_src': imageSrc, 'desc': description, 'price': price, 'name': name, 'qty': quantity,'product_Id':product_Id})
        
        else:

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
            return render(request,'checkout.html')
        
    cart_product_list = request.session.get('cart_product_list', [])
    new_cart_product_list = request.session.get('new_cart_product_list',[])
    bool_storer = request.session.get('bool_storer',[])
    return render(request,'checkout.html',{"firstBool":bool_storer[0],"secondBool":bool_storer[1],"cart_product_list":cart_product_list,"new_cart_product_list":new_cart_product_list})

def orders(request):
    orders = Order.objects.all()
    orderUpd = OrderUpdate.objects.all()

    prodList = []
    items_In_cartProd = CartProd.objects.all()
    for item in items_In_cartProd:
        itemJson = item.itemJson.strip()

        if itemJson:
            data = json.loads(itemJson)

        else:
            data = {}

        for key in data:
            prodId = key
            prodList.append({"prodId":prodId}) 
    
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

    return render(request, 'Orders.html', {'product_list': product_list,'prodList':json.dumps(prodList)})


def cart(request):

    new_prodId = ''
    prodId = ''
    prods = ''
    existing_prods = ''
    prodCart = CartProd.objects.all()

    if len(prodCart) != 0:

        cart_product_list = []    

        for existing_prods in prodCart:

            item_json = existing_prods.itemJson.strip()

            if item_json:

                try:
                    data = json.loads(item_json)
                except json.JSONDecodeError as e:
                    data = {}

            else:

                data = {}

            for key in data:

                prodId = key
                product_key = tuple(data[key])
                imageSrc = product_key[1]
                description = product_key[4]
                price = product_key[3]
                name = product_key[2]
                quantity = product_key[0]
                cart_product_list.append({'image_src': imageSrc, 'desc': description, 'price': price, 'name': name, 'qty': quantity,'prodId':prodId})

    if request.method == "POST":

        data = json.loads(request.body)
        itemJson = data.get("itemJson", '')
        newJson = json.dumps(itemJson).replace("'", "\"")
        new_data = json.loads(newJson)

        for new_key in new_data:
            new_prodId = new_key
            new_name = new_data[new_key][2]

        if new_name != None:    
            prodInCart = CartProd(itemJson=newJson)
            prodInCart.save()

    new_prodCart = CartProd.objects.all()

    cart_product_list = []

    for prods in new_prodCart:

        item_json = prods.itemJson.strip()

        if item_json:
            try:
                data = json.loads(item_json)
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {str(e)}")
                data = {}
        else:
            data = {}

        for key in data:
            new_prod_Id = key
            product_key = tuple(data[key])
            imageSrc = product_key[1]
            description = product_key[4]
            price = product_key[3]
            name = product_key[2]
            quantity = product_key[0]
            cart_product_list.append({'image_src': imageSrc, 'desc': description, 'price': price, 'name': name, 'qty': quantity,'prodId':new_prod_Id})

    if existing_prods != '':
        
        for existing_prods in prodCart:

            item_json = existing_prods.itemJson.strip()

            if item_json:
                try:
                    data = json.loads(item_json)
                except json.JSONDecodeError as e:
                    print(f"JSONDecodeError: {str(e)}")
                    data = {}
            else:
                data = {}

            for key in data:
                prodId = key

                if new_prodId == prodId:
                    existing_prods.delete()

    return render(request,'cart.html',{'cart_product_list':cart_product_list,'newCartProdList':json.dumps(cart_product_list)})
