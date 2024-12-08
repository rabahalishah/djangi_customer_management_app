from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm
from .filters import *

from django.forms import inlineformset_factory
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allow_users
from django.contrib.auth.models import Group

# Create your views here.


@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            messages.success(request, 'Account was created for ' + user)
            return redirect('login')

    context = {'form': form}
    return render(request, "accounts/login", context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'username or password is incorrect!')
            context = {}
            return render(request, 'accounts/login.html', context)
    context = {}
    return render(request, "accounts/login", context)


def logoutUser(request):
    logout(request)

    return redirect('login')


@login_required(login_url='login')  # this gonna run first
@allow_users(allowed_roles=['admin'])  # then this is gonna run
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customer = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {
        'customers': total_customer,
        'total_orders': total_orders,
        'delivered': delivered,
        'pending': pending,
    }

    return render(request, "accounts/dashboard.html", context)


@login_required(login_url='login')
def products(request):
    return render(request, "accounts/products.html")


@login_required(login_url='login')
@allow_users(allowed_roles=['customer'])
def userPage(request):

    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    context = {'orders': orders,
               'total_orders': total_orders,
               'delivered': delivered,
               'pending': pending, }
    return render(request, "accounts/userPage.html", context)


@login_required(login_url='login')
@allow_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    context = {}
    return render(request, "accounts/account_setting.html", context)


@login_required(login_url='login')
@allow_users(allowed_roles=['admin'])
def customers(request, pk_test):
    customer = Customer.objects.get(id=pk_test)

    # extracting orders for this specific customer
    orders = customer.order_set.all()
    order_count = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {'customer': customer, 'orders': orders}

    return render(request, "accounts/customer.html", context)


@login_required(login_url='login')
def createOrder(request, pk):

    OrderFormSet = inlineformset_factory(
        Customer, Order, fields=('product', 'status'))
    # OrderFormSet = inlineformset_factory(Parent Model, Chile Model)

    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)

    if request.method == 'POST':
        # here reques.POST contains all the data that user has entered from the frontend

        formset = OrderFormSet(request.POST, instance=customer)

        if formset.is_valid():
            formset.save()
            return redirect('/')

    context = {'form': formset}

    # return render(request, "accounts/order_form.html", context)
    return


@login_required(login_url='login')
def updateOrder(request, pk):

    # reteriving the saved data
    order = Order.objects.get(id=pk)

    # since we are updating the data, so already present data must be filled there already
    form = OrderForm(instance=order)

    if request.method == 'POST':
        # here reques.POST contains all the data that user has entered from the frontend
        print('Printing POST:', request.POST)

        form = OrderForm(request.POST, instance=order)

        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form': form}
    # return render(request, "accounts/order_form.html", context)
    return


@login_required(login_url='login')
@allow_users(allowed_roles=['admin'])
def deleteOrder(request, pk):

    # reteriving the saved data
    order = Order.objects.get(id=pk)

    if request.method == 'POST':
        # here reques.POST contains all the data that user has entered from the frontend
        print('Printing POST:', request.POST)

        order.delete()
        return redirect('/')

    context = {'item': order}
    # return render(request, "accounts/order_form.html", context)
    return
