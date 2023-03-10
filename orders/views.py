from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from cart.models import CartItem,Cart
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import random
from cart.views import _cart_id
from accounts.models import UserProfile
# Create your views here.

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()
    
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    
    cart_items = CartItem.objects.filter(user=request.user)
    
    for item in cart_items:
        orderproduct               = OrderProduct()
        orderproduct.order_id      = order.id
        orderproduct.payment       = payment
        orderproduct.user_id       = request.user.id
        orderproduct.product_id    = item.product_id
        orderproduct.quantity      = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered       = True
        orderproduct.save()
        
        cart_item          = CartItem.objects.get(id=item.id)
        product_variation  = cart_item.variations.all()
        orderproduct       = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()
        
    # reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
        
    #clear cart
    cart = Cart.objects.get(cart_id = _cart_id(request))
    cart.delete()
    CartItem.objects.filter(user=request.user).delete()
    
    #send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()   
    
    #send order number and transaction id back to sendData method via Json response
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data) #it came from payments.html - sendData()
    
    #return render(request, 'orders/payments.html')
    
    

    
def place_order(request,total=0,quantity =0,order=None,coupon_obj=None):
    # current_user = request.user
    # total=0 
    # quantity=0
    # # If the cart count is less than or equal to 0, then redirect back to shop
    # cart_items = CartItem.objects.filter(user=current_user)
    # cart_count = cart_items.count()
    # if cart_count <= 0:
    #     return redirect('store')
    
    # grand_total = 0
    # tax = 0
    # for cart_item in cart_items:
    #     quantity += cart_item.quantity
    #     if cart_item.product.is_offer:
    #         total+=(cart_item.product.offered_price * cart_item.quantity)
    #     else:
    #         total+=(cart_item.product.price * cart_item.quantity)
    # tax = (2 * total)/100
    # grand_total = total + tax
    
    
    # if request.method == 'POST':
    #     form = OrderForm(request.POST)
    #     if form.is_valid():
    #         # Store all the billing information inside Order table
    #         data                = Order()
    #         data.user           = current_user
    #         data.first_name     = form.cleaned_data['first_name']
    #         data.last_name      = form.cleaned_data['last_name']
    #         data.phone          = form.cleaned_data['phone']
    #         data.email          = form.cleaned_data['email']
    #         data.address_line_1 = form.cleaned_data['address_line_1']
    #         data.address_line_2 = form.cleaned_data['address_line_2']
    #         data.country        = form.cleaned_data['country']
    #         data.state          = form.cleaned_data['state']
    #         data.pincode        = form.cleaned_data['pincode']
    #         data.city           = form.cleaned_data['city']
    #         data.order_note     = form.cleaned_data['order_note']
    #         data.order_total    = grand_total
    #         data.tax            = tax
    #         data.ip             = request.META.get('REMOTE_ADDR')#to get current user ip
    #         data.save()#use to create a primary key or id no to generate orderid
    #         yr = int(datetime.date.today().strftime('%Y'))
    #         dt = int(datetime.date.today().strftime('%d'))
    #         mt = int(datetime.date.today().strftime('%m'))
    #         d  = datetime.date(yr,mt,dt)
    #         current_date = d.strftime("%Y%m%d") #2023 01 15
    #         order_number = current_date + str(data.id)
    #         data.order_number = order_number
    #         data.save()
            
    #         order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
    #         context = {
    #             'order': order,
    #             'cart_items': cart_items,
    #             'total': total,
    #             #'coupon': coupon,
    #             'tax': tax,
    #             'grand_total': grand_total,
    #         }
    #         return render(request, 'orders/payments.html', context)
            
    #     else:
    #         return redirect('checkout')
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    carts=Cart.objects.filter(cart_id=_cart_id(request)).first()
    cart=CartItem.objects.get(user=current_user,cart=carts)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    data = Order()
    tax=0
    grand_total=0
    for cart_item in cart_items:
        print(cart_item.quantity)
        #total+=(cart_item.product.price * cart_item.quantity)
        quantity+= cart_item.quantity
        if cart_item.product.is_offer:
            total+=(cart_item.product.offered_price * cart_item.quantity)
        else:
            total+=(cart_item.product.price * cart_item.quantity)
            
        data.product_id=cart_item.product_id
        data.quantity=cart_item.quantity
        data.product_price=cart_item.product.price
        data.save()
    if cart.coupon:
            if cart.coupon.min_amount<cart.sub_total():
                total=total-cart.coupon.amount

    tax=(0.02)*(total) 
    grand_total=total+tax
    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        #print(form)
        print (form.errors)
        if form.is_valid():
            print('HELLO')
            address = UserProfile.objects.get(pk = request.POST.get('address'))
            #store all the billing info in table
            data.user=current_user
            data.address=address

            data.order_note=form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            #generate order id
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number=current_date + str(data.id)
            data.order_number = order_number
            data.save()  
            
            order = Order.objects.get(user=current_user,is_ordered= False,order_number = order_number)
           
            #user = User.objects.get(user=current_user)
            #address = Address.objects.get(user_id=request.user.id)
        context ={
            'order':order,
            'cart_items':cart_items,
            # 'cart_items':cart,
            'total':total,
            'cart':cart,
            'tax':tax , 
            'grand_total':grand_total,
                #'user':user,
                #'address':address,         
            }
            
        return render(request,'orders/payments.html',context)     
    else:
        return redirect('checkout')
        
def cancel(request,order_id,value):
    order = Order.objects.filter(order_number=order_id).get()
    if value == 0:
        order.status = 'Cancelled'
        order.save()
    if value == 1:
        order.status = 'Returned'
        order.save()
    return redirect(f"/accounts/order_detail/{order_id}/")

        
def order_complete(request):
    
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
        #coupon = CouponDetail.objects.filter(user=request.user)
        # for i in coupon:
        #     coupon=i
        
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        
        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
            # 'coupon':coupon,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
    
    
def cod(request,order_number):
    print(request.user)
    
    order = Order.objects.get(user=request.user, is_ordered=False,order_number=order_number)
    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = random.randint(111111,999999),
        payment_method = "Cash on Delivery",
        amount_paid = order.order_total,
        status = "Placed",
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()
    cart = Cart.objects.filter(cart_id = _cart_id(request))
    cart.delete()
    
    
    return render(request, 'orders/cod_success.html')
    