from .forms import TenantForm
from django_tenants.utils import schema_context
from django.contrib.auth import login
from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from .models import *  
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django_tenants.utils import schema_context
from django.core.management import call_command
from django.conf import settings
from a_tenant_manager.models import *

# Create your views here.

def tenant (request):
    tenant_form = TenantForm()

    if request.method == "POST":
        tenant_form = TenantForm(request.POST)
        if tenant_form.is_valid():
            tenant = tenant_form.save()
            call_command('migrate_schemas', schema_name=tenant.schema_name)

            domain = Domain.objects.create(
                tenant=tenant,
                domain=f"{tenant.schema_name}.{settings.BASE_URL}",
                is_primary= True

            )

            TenantMember.objects.create(
                user = request.user,
                tenant = tenant,
                is_admin = True
            )

            with schema_context(tenant.schema_name):
                request.user.backend = 'allauth.account.auth_backends.AuthenticationBackend'
                login(request, request.user)
            return redirect(f"http://{domain.domain}{settings.PORT}")
    try:
        tenant_member = TenantMember.objects.get(user=request.user, tenant=request.tenant)
    except:
        tenant_member = None

    if request.user.is_authenticated:
        user_tenants = TenantMember.objects.filter(user=request.user)
    else:
        user_tenants =[]

    base_domain = f"{settings.BASE_URL}{settings.PORT}"

    context = {
        'tenant_form': tenant_form,
        'tenant_member': tenant_member,
        'user_tenants': user_tenants,
        'base_domain': base_domain,
        
    }
    return render(request, 'tenants/tenant.html', context)

def tenant_landing(request):
    try:
        tenant_member = TenantMember.objects.get(user=request.user, tenant=request.tenant)
    except TenantMember.DoesNotExist:
        tenant_member = None

    context = {
        'tenant_member': tenant_member,
    }
    return render(request, 'tenants/tenant_landing.html', context)


def search(request):
    if request.method == "POST":
        searched  = request.POST["searched"]
        keys = Product.objects.filter(name__contains = searched)
        if request.user.is_authenticated:
            customer = request.user
            order, created = Order.objects.get_or_create(customer =customer,complete =False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
    else:
        items =[]
        order ={'get_cart_items' :0,'get_cart_total':0}
        cartItems = order['get_cart_items']
    products = Product.objects.all()
    return render(request,'app/search.html',{"searched":searched,"keys":keys,'products' : products,'cartItems':cartItems})

def register(request):
    form = CreateUserForm()
    context = {'form':form}
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
    context ={'form':form}
    return render(request,'app/register.html',context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request,user)
            return redirect('tenant_landing')
        else: messages.info(request,'username or password not correct!')

    context = {}
    return render(request,'app/login.html',context)
def logoutPage(request):
    logout(request)
    return redirect('login')
def home(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer =customer,complete =False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items =[]
        order ={'get_cart_items' :0,'get_cart_total':0}
        cartItems = order['get_cart_items']
    products = Product.objects.all()
    context = {'products' : products,'cartItems':cartItems}
    return render(request,'app/home.html',context)
def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer =customer,complete =False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items =[]
        order ={'get_cart_items' :0,'get_cart_total':0}
        cartItems = order['get_cart_items']
    context = {'items':items,'order':order,'cartItems':cartItems}
    return render(request,'app/cart.html',context)
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer =customer,complete =False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items =[]
        order ={'get_cart_items' :0,'get_cart_total':0}
        cartItems = order['get_cart_items']
    context = {'items':items,'order':order,'cartItems':cartItems}
    return render(request,'app/checkout.html',context)
    
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer =customer,complete =False)
    orderItem, created = OrderItem.objects.get_or_create(order =order,product = product)
    if action =='add':
        orderItem.quantity +=1
    elif action =='remove':
        orderItem.quantity -=1
    orderItem.save()
    if orderItem.quantity<=0:
        orderItem.delete()
    return JsonResponse('added',safe=False)

