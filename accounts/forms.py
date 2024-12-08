from django.forms import ModelForm
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        # fields = ['customer', product]  # if you want to include only specific fields
        fields = '__all__'
        exclude = ['user']


class OrderForm(ModelForm):
    class Meta:
        model = Order
        # fields = ['customer', product]  # if you want to include only specific fields
        fields = '__all__'


# modifying Django UserCreationForm according to our need
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
