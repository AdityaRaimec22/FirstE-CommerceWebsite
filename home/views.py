from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.core.mail import send_mail, EmailMessage
from FirstWebsite import settings
from . models import Product, Contact, Order, CartProd, Return, Address
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from math import ceil
from django.views.decorators.csrf import csrf_exempt
from . tokens import generate_token
from PayTm import CheckSum
# from datetime import datetime
import json

MERCHANT_KEY = 'kbzk1DSbJiV_03p5'
def signin(request):
    fname = ''
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['pass1']

        user = authenticate(username=username, password=password)

        if user is not None and check_password(password, user.password):
            login(request, user)
            fname = user.first_name

            # Store fname value in session
            request.session['fname'] = fname

            # print("the first name of the user is:",fname)
            messages.success(request, "You are logged in successfully")
            return redirect('home')
        else:
            messages.error(request, "Bad Credentials")
            return redirect('signin')

    return render(request, 'signin.html', {'fname': fname})

# @login_required(login_url="/signin")
def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if pass1 != pass2:
            messages.error(request,"Password and confirm password were not matched")
            return redirect('signup')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.save()

        messages.success(request, "Your account has been successfully created!! kindly logIn to continue. Thanks")

        subject = "Welcome to raimart login!"
        message = "Hello " + myuser.first_name + "!\n\n"+"Welcome to raimart!!\n Thanks for visiting our site.\n We have also sent you a confirmation email kindly confirm your email after clicking on the link present there.\n\nThanking You\nAditya Rai"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list)

        current_site = get_current_site(request)
        email_subject = "Confirm your email @raimart"
        message2 = render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('signin')

    return render(request, 'signup.html')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk = uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        messages.success(request,"Your account has been activated.")
        return redirect('/')
    else:
        return render(request,'activation_failed.html')


def userLogout(request):
    logout(request)
    messages.success(request,"Logged Out Successfully")
    return redirect('home')

def home(request):

    user = request.user

    allProds = []
    catProds = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catProds}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    prodList = []
    try:
        items_In_cartProd = CartProd.objects.filter(user=user)
    except:
        items_In_cartProd = CartProd.objects.all()
    for item in items_In_cartProd:
        itemJson = item.itemJson.strip()

        if itemJson:
            data = json.loads(itemJson)
        else:
            data = {}

        for key in data:
            prodId = key
            prodList.append({"prodId": prodId})

    # Retrieve fname from session
    fname = request.session.get('fname')

    return render(request, 'home.html', {'prodList': json.dumps(prodList), 'allprods': allProds, 'fname': fname})

def searchMatch(query , item):
    if query in item.product_name.lower() or query in item.desc.lower() or query in item.category.lower():
        return True
    else:
        return False
        
def search(request):

    user = request.user

    query = request.GET.get('search')
    prods = []
    catProds = Product.objects.values('category','id')
    cats = {item['category'] for item in catProds}
    for cat in cats:
        prodTemp = Product.objects.filter(category = cat)
        prod = [item for item in prodTemp if searchMatch(query , item)]
        prods.append(prod)

    prodList = []
    items_In_cartProd = CartProd.objects.filter(user=user)
    for item in items_In_cartProd:
        itemJson = item.itemJson.strip()

        if itemJson:
            data = json.loads(itemJson)

        else:
            data = {}

        for key in data:
            prodId = key
            prodList.append({"prodId":prodId})

    fname = request.session.get('fname')
            
    params = {'prods':prods,'prodList':json.dumps(prodList),'fname':fname}

    return render(request,'search.html',params)

def products(request,myid):

    user = request.user

    product = Product.objects.filter(id=myid)
    prodList = []
    items_In_cartProd = CartProd.objects.filter(user=user)
    if request.path == reverse('home'):
        return HttpResponseRedirect(reverse('home'))
    for item in items_In_cartProd:
        itemJson = item.itemJson.strip()

        if itemJson:
            data = json.loads(itemJson)

        else:
            data = {}

        for key in data:
            prodId = key
            prodList.append({"prodId":prodId})

    fname = request.session.get('fname')
    return render(request,'products.html',{'product':product[0], 'prodList':json.dumps(prodList),'fname':fname})

@login_required(login_url="/signin")
def contact(request):

    user = request.user

    if request.method == "POST":
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        desc = request.POST.get('desc','')
        contact = Contact(name=name,email=email,phone=phone,desc=desc)
        contact.save()

    prodList = []
    items_In_cartProd = CartProd.objects.filter(user=user)
    for item in items_In_cartProd:
        itemJson = item.itemJson.strip()

        if itemJson:
            data = json.loads(itemJson)

        else:
            data = {}

        for key in data:
            prodId = key
            prodList.append({"prodId":prodId})

    fname = request.session.get('fname')
    return render(request,'contact.html',{'prodList':json.dumps(prodList),'fname':fname})

@login_required(login_url="/signin")
def checkout(request):

    user = request.user

    # cart_product_list = []
    # new_cart_product_list = []
    # bool_storer = []
    # idstr = ''
    if request.method == "POST":
        
        # user = request.user

        cart_product_list = []
        new_cart_product_list = []
        bool_storer = []
        idstr = ''

        data = request.POST.get('requestBody')
        idstr = request.POST.get('idstr')
        prodCart = CartProd.objects.filter(user=user)
        
        if data == '1':
            # print("request made from cart")

            request.session['bool_storer'] = bool_storer
            bool_storer.append(True)
            bool_storer.append(False)
            

            if len(prodCart) != 0:
                # print("cart ki length 0 se jyada hai")

                request.session['cart_product_list'] = cart_product_list  

                for existing_prods in prodCart:

                    item_json = existing_prods.itemJson.strip()

                    if item_json:
                        try:
                            data = json.loads(item_json)
                            print("Bhai sb shi hai")
                        except json.JSONDecodeError as e:
                            print("error is:",e)
                            data = {}
                    else:
                        # print("Are me execute ho gya aur json string load hi nhi ho payi.")
                        data = {}

                    for key in data:
                        try:
                            # print("try statement executed")
                            prodId = key
                            product_key = tuple(data[key])
                            imageSrc = product_key[1]
                            description = product_key[4]
                            price = product_key[3]
                            name = product_key[2]
                            quantity = product_key[0]
                            # print(imageSrc,description,price,name,quantity)
                            cart_product_list.append({'image_src': imageSrc, 'desc': description, 'price': price, 'name': name, 'qty': quantity,'prodId':prodId})
                        except:
                            # print("except statement executed")
                            pass

        elif data == '2':
            # print("request made from products page")

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
                            try:
                                product_Id = key
                                product_key = tuple(data[key])
                                imageSrc = product_key[1]
                                description = product_key[4]
                                price = product_key[3]
                                name = product_key[2]
                                quantity = product_key[0]
                                new_cart_product_list.append({'image_src': imageSrc, 'desc': description, 'price': price, 'name': name, 'qty': quantity,'product_Id':product_Id})
                            except:
                                pass

    addList = []
    addresses = Address.objects.filter(user=user)
    for newAdd in addresses:
        
        user_name = newAdd.name.strip()
        user_phone = newAdd.phone.strip()
        user_pincode = newAdd.pincode.strip()
        user_city = newAdd.city.strip()
        user_street = newAdd.street.strip()
        user_state = newAdd.state.strip()
        addList.append({'name':user_name,'phone':user_phone,'pincode':user_pincode,'city':user_city,'street':user_street,'state':user_state})

    
    cart_product_list = request.session.get('cart_product_list', [])
    new_cart_product_list = request.session.get('new_cart_product_list',[])

    bool_storer = request.session.get('bool_storer',[])

    fname = request.session.get('fname')
    return render(request,'checkout.html',{"firstBool":bool_storer[0] if bool_storer else True,"secondBool":bool_storer[1] if bool_storer else False,"cart_product_list":cart_product_list,"new_cart_product_list":new_cart_product_list,"fname":fname,'addList':addList})

@login_required(login_url="/signin")
def orders(request):

    user = request.user

    orders = Order.objects.filter(user=user)
    prodReturn = Return.objects.filter(user=user)

    prodReturnList = []
    for prods in prodReturn:
        returnId = prods.returnId
        prodReturnList.append(returnId)
    # orderUpd = OrderUpdate.objects.filter(user=user)

    prodList = []
    items_In_cartProd = CartProd.objects.filter(user=user)
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
    # for things in orderUpd:
    #     prodDesc = things.update_desc.strip()
    #     Time = things.timestamp

    for order in orders:

        item_json = order.itemJson.strip()
        order_id = order.order_id
        prodDesc = order.order_Update.strip()
        Date = order.Time
        # Time = order.current_Time.strip()


        if item_json:
            try:
                data = json.loads(item_json)
            except json.JSONDecodeError as e:
                # print(f"JSONDecodeError: {str(e)}")
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
            product_list.append({'image_src': imageSrc, 'desc': description, 'price': price, 'name': name, 'qty': quantity,'prodDesc':prodDesc, 'Date':Date,'Id':order_id})

    fname = request.session.get('fname')
    return render(request, 'Orders.html', {'product_list': product_list,'prodList':json.dumps(prodList),'fname':fname,'prodReturnList':prodReturnList})

@login_required(login_url="/signin")
def cart(request):

    user = request.user
    new_prodId = ''
    prodId = ''
    prods = ''
    existing_prods = ''
    prodCart = CartProd.objects.filter(user=user)
    # prodCart = CartProd.objects.all()

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
            prodInCart = CartProd(user=user, itemJson=newJson)
            prodInCart.save()

    new_prodCart = CartProd.objects.filter(user = user)

    cart_product_list = []

    for prods in new_prodCart:

        item_json = prods.itemJson.strip()

        if item_json:
            try:
                data = json.loads(item_json)
            except json.JSONDecodeError as e:
                # print(f"JSONDecodeError: {str(e)}")
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
                    # print(f"JSONDecodeError: {str(e)}")
                    data = {}
            else:
                data = {}

            for key in data:
                prodId = key

                if new_prodId == prodId:
                    existing_prods.delete()

    fname = request.session.get('fname')

    return render(request,'cart.html',{'cart_product_list':cart_product_list,'newCartProdList':json.dumps(cart_product_list),'fname':fname})

def prodReturn(request):
    user = request.user
    prodList = []
    ordId = 0
    order_id = 0
    new_Update = ''
    items_In_cartProd = CartProd.objects.filter(user=user)
    orderFound = False
    prod_Return = Return(user=user,name= '', email='', phone=0, returnId=0,desc='')

    if request.method == "POST":
        name = request.POST.get('name','')
        number = request.POST.get('phone','')
        email = request.POST.get('email','')
        order_id = request.POST.get('Id',0)
        desc = request.POST.get('desc','')
        prod_Return = Return(user=user,name= name, email=email, phone=number, returnId=order_id,desc=desc)
        
    ordList = []
    existing_Orders = Order.objects.filter(user = user)
    for order in existing_Orders:
        ordId = order.order_id
        ordList.append(ordId)
            # newUpdate = order.order_Update.strip()
        print("ordId is:",ordId)
        print("order_id is:",order_id)

        if str(ordId) == str(order_id):
            new_Update = "Return requested2"
            print("things working fine")
            instance = existing_Orders.get(order_id = ordId)
            instance.order_Update = new_Update
            instance.save()
            prod_Return.save()
            orderFound = True
            break

        else:
            orderFound = False
            print("me toh else me aa gya batao kya krna hai..")
        # UpdateDesc = Order(user=user,order_Update = new_Update)
        # UpdateDesc.save()

    print(order.order_Update.strip())

    for item in items_In_cartProd:
        itemJson = item.itemJson.strip()

        if itemJson:
            data = json.loads(itemJson)

        else:
            data = {}

        for key in data:
            prodId = key
            prodList.append({"prodId":prodId})

    fname = request.session.get('fname')
    print("the found is:",orderFound)

    return render(request, 'return.html',{'prodList':json.dumps(prodList),'fname':fname,'orderFound':orderFound,'ordList':ordList})

@csrf_exempt
def paytm(request):

    user = request.user
    param_dict = {}

    if request.method == "POST":
        print("the request is made")
        request.session['param_dict'] = param_dict
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return HttpResponseBadRequest("Invalid JSON data")

        itemJson = data.get('itemJson', '')
        name = data.get('name', '')
        email = data.get('email', '')
        address = data.get('address1', '') + " " + data.get('address2', '')
        city = data.get('city', '')
        state = data.get('state', '')
        phone_number = data.get('phone_number', 0)
        zip_code = data.get('zip_code', 0)
        update_desc = "Your Order has been placed successfully. Thanks for ordering with us!!"
        # Time = datetime.now()

        userOrder = Order(
            user=user,
            itemJson=itemJson,
            name=name,
            email=email,
            address=address,
            city=city,
            state=state,
            phone_number=phone_number,
            zip_code=zip_code, 
            order_Update = update_desc
            # current_Time = Time
        )
        userOrder.save()

        # print("The order Id is:",userOrder.order_id)
        # update = OrderUpdate(user=user,order_id = userOrder.order_id, update_desc = "The Order has been Placed.")
        # update.save()

        param_dict['MID'] = 'XiwOUO11217750221275'
        param_dict['ORDER_ID'] = str(userOrder.order_id)
        param_dict['TXN_AMOUNT'] = '1'
        param_dict['CUST_ID'] = email
        param_dict['INDUSTRY_TYPE_ID'] = 'Retail'
        param_dict['WEBSITE'] = 'WEBSTAGING'
        param_dict['CHANNEL_ID'] = 'WEB'
        param_dict['CALLBACK_URL'] = 'http://127.0.0.1:8000/home/cart/handlerequest'
    
    param_dict = request.session.get('param_dict',{})
    # print("hm bhi execute hue hai lala:",param_dict)
    return render(request, 'paytm.html',{'param_dict':param_dict})
    
@csrf_exempt
def handlerequest(request):
    print("me execute ho gya.")
    return HttpResponse('done')
    #paytm will send post request here.

@login_required(login_url="/signin")
def address(request):

    user = request.user
    fname = request.session.get('fname')
    items_In_cartProd = CartProd.objects.filter(user=user)
    prodList = []
    for item in items_In_cartProd:
        itemJson = item.itemJson.strip()

        if itemJson:
            data = json.loads(itemJson)

        else:
            data = {}

        for key in data:
            prodId = key
            prodList.append({"prodId":prodId})

    if request.method == "POST":
        name = request.POST.get('name','') 
        Phone = request.POST.get('Phone','') 
        street = request.POST.get('Address','')
        city = request.POST.get('City','')
        state = request.POST.get('State','')
        pincode = request.POST.get('Zip','')
        address = Address(user=user, name = name, phone = Phone, city = city, pincode = pincode, state = state, street = street)
        address.save()

    addList = []
    addresses = Address.objects.filter(user=user)
    for newAdd in addresses:
        
        user_name = newAdd.name.strip()
        user_phone = newAdd.phone.strip()
        user_pincode = newAdd.pincode.strip()
        user_city = newAdd.city.strip()
        user_street = newAdd.street.strip()
        user_state = newAdd.state.strip()
        addList.append({'name':user_name,'phone':user_phone,'pincode':user_pincode,'city':user_city,'street':user_street,'state':user_state})
    
    return render(request,'address.html',{'fname':fname,'prodList':prodList,'addList':addList})
    

