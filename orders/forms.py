from django import forms
from .models import Order

class OrderForm(forms.ModelForm):#it gives you replication of model itself thats y use it
    class Meta:
        model = Order
        fields = ['first_name','last_name', 'phone','email', 'address_line_1','address_line_2','country','state','city','order_note']#if pincode needed can be added
        