from django.shortcuts import render,redirect,get_object_or_404
from .models import Cart,Product,CartItem
from store.models import Variation
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Coupon, UsedCoupon
from accounts.models import UserProfile
from accounts.forms import UserProfileForm,AddressForm
# Create your views here.

def _cart_id(request):
    cart     = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    current_user=request.user
    product     = Product.objects.get(id=product_id) #get the product
    #if user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key   = item
                value = request.POST[key]
            
                # print(key, value)
                try:
                    variation      =Variation.objects.get(product = product, variation_category__iexact = key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

    
        

    
        #getting the cartitem 
        is_cart_item_exists         = CartItem.objects.filter(product = product, user = current_user).exists()
        if is_cart_item_exists:   
    
            cart_item           = CartItem.objects.filter(product = product, user = current_user)#return cartitem objects
            if product.stock<=cart_item[0].quantity:
                messages.error(request,'Out of stock')
                return redirect('cart')
            
            ex_var_list = []
            id          = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            
            
            if product_variation in ex_var_list:
                #increase cart item quantity
                index          = ex_var_list.index(product_variation)
                item_id        = id[index]
                item           = CartItem.objects.get(product = product, id =item_id)
                item.quantity += 1
                item.save()
                
            else:
                
                item = CartItem.objects.create(product = product,quantity=1, user = current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                
                    item.variations.add(*product_variation)
            
                item.save()
            
        else: 
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()
            cart_item      = CartItem.objects.create(
                product    = product,
                quantity   = 1,
                user       = current_user,
                cart=cart,
            )
            
            if len(product_variation) > 0:
                cart_item.variations.clear()
                    
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
        #user is not autheticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key   = item
                value = request.POST[key]
            
                # print(key, value)
                try:
                    variation      =Variation.objects.get(product = product, variation_category__iexact = key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        
            #getting the cart
            try:
                cart    = Cart.objects.get(cart_id =_cart_id(request))#get the cart using the cart_id present in the session
            except Cart.DoesNotExist:
                cart    = Cart.objects.create(
                cart_id = _cart_id(request)
                )
            cart.save()
        
        #getting the cartitem 
        is_cart_item_exists         = CartItem.objects.filter(product = product, cart = cart).exists()
        if is_cart_item_exists:   
        
                cart_item           = CartItem.objects.filter(product = product, cart = cart) #return cartitem objects
                #existing variation -- database
                #current variation  -- product variation list
                #item_id            -- database
                
                ex_var_list = []
                id          = []
                for item in cart_item:
                    existing_variation = item.variations.all()
                    ex_var_list.append(list(existing_variation))
                    id.append(item.id)
                
                
                if product_variation in ex_var_list:
                    #increase cart item quantity
                    index          = ex_var_list.index(product_variation)
                    item_id        = id[index]
                    item           = CartItem.objects.get(product = product, id =item_id)
                    item.quantity += 1
                    item.save()
                    
                else:
                    item = CartItem.objects.create(product = product,quantity=1, cart = cart)
                    if len(product_variation) > 0:
                        item.variations.clear()
                    
                        item.variations.add(*product_variation)
                
                    item.save()
                
        else: 
                cart =   Cart.objects.create(cart_id = _cart_id(request))
                cart.save()
                cart_item      = CartItem.objects.create(
                    product    = product,
                    quantity   = 1,
                    user=request.user,
                    cart       = cart,
                )
                
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                        
                    cart_item.variations.add(*product_variation)
                cart_item.save()
        return redirect('cart')

def remove_cart(request, product_id, cart_item_id):         #function for decreasing item one by one
    #cart       = Cart.objects.get(cart_id =_cart_id(request))
    product    = get_object_or_404(Product, id = product_id )
    try:
        if request.user.is_authenticated:
            cart_item  = CartItem.objects.get(product = product, user = request.user, id=cart_item_id)
        else:
            cart      = Cart.objects.get(cart_id      = _cart_id(request))
            cart_item  = CartItem.objects.get(product = product, cart = cart, id=cart_item_id)
        if cart_item.quantity   > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart.delete()
            cart_item.delete()
            
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):        #function for removing all items together
    #cart      = Cart.objects.get(cart_id      = _cart_id(request))
    product   = get_object_or_404(Product, id = product_id)
    if request.user.is_authenticated:
        cart_item  = CartItem.objects.get(product = product, user = request.user, id=cart_item_id)
    else:
        cart      = Cart.objects.get(cart_id      = _cart_id(request))
        cart_item = CartItem.objects.get(product  =product, cart=cart, id = cart_item_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart.delete()
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax        =0
        grand_total=0
        if request.user.is_authenticated:
            cart_items    = CartItem.objects.filter(user = request.user,is_active = True)  #for logged in users
        else:
            cart          = Cart.objects.get(cart_id     = _cart_id(request))              #for non logged in users
            cart_items    = CartItem.objects.filter(cart = cart,is_active = True)
        for cart_item in cart_items:
            product = Product.objects.get(pk = cart_item.product.id)
            if product.stock<cart_item.quantity:
                cart_item.delete()
                return redirect('cart')
            else:
                quantity+= cart_item.quantity       
                if cart_item.product.is_offer:
                    total+=(cart_item.product.offered_price * cart_item.quantity)
                else:
                    total+=(cart_item.product.price * cart_item.quantity)
        tax           = (2 * total)/100
        grand_total   = total + tax
        
    except ObjectDoesNotExist:
        pass #just ignore
    
    context ={
        'total'      : total,
        'quantity'   :quantity,
        'cart_items' :cart_items,
        'tax'        :tax,
        'grand_total':grand_total,
    }
    
    return render(request, 'store/cart.html',context)

@login_required(login_url='login')
def checkout(request ,total=0, quantity=0, cart_items=None):
    try:
        tax        =0
        grand_total=0
        address_form = AddressForm()
        user=request.user
        address=UserProfile.objects.filter(user=request.user)
        if request.user.is_authenticated:
            print("ooo")
            cart_items    = CartItem.objects.filter(user = request.user,is_active = True)#for logged in users
            print("1")
            carts         = Cart.objects.filter(cart_id = _cart_id(request)).first()
            print(carts)
            print(request.user)
            cart          = CartItem.objects.all().get(user = request.user,cart = carts)
            print("3")
        else:
            print("FOR")
            cart          = Cart.objects.get(cart_id     = _cart_id(request))              #for non logged in users
            cart_items    = CartItem.objects.filter(cart = cart,is_active = True)
        for cart_item in cart_items:
            quantity += cart_item.quantity
            if cart_item.product.is_offer:
                total    += (cart_item.product.offered_price * cart_item.quantity)
            else:
                total    += (cart_item.product.price * cart_item.quantity)

            print(total)
        if cart_item.product.is_offer:
            pass
        else:
            if cart.coupon:
                if cart.coupon.used<cart.coupon.max_use:
                    cart.coupon.is_expired=True
                    cart.coupon.save()
                if cart.coupon.min_amount<cart.sub_total():
                    total=total-cart.coupon.amount
                    print(total)
        tax           = (2 * total)/100
        grand_total   = total + tax
        print(grand_total)
        
    except ObjectDoesNotExist:
        print("HEELO")
    
    context ={
        'total'      : total,
        'quantity'   :quantity,
        'cart_items' :cart_items,
        'tax'        :tax,
        'grand_total':grand_total,
        'address':address,
        'address_form':address_form,
        'cart':cart,
    }
    return render(request, 'store/checkout.html', context)


def apply_coupon(request):
    if request.method == 'POST':
        code =  request.POST['coupon']
        try:
            coupon = Coupon.objects.get(code__iexact = code) 
            carts = Cart.objects.get(cart_id = _cart_id(request))
            cart  = CartItem.objects.get(user = request.user,cart = carts)
            if cart.product.is_offer:
                messages.warning(request,'Coupon Cannot Apply')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            if cart.coupon:
                messages.warning(request,'Coupon Applied')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            if cart.get_cart_total() < coupon.min_amount:
                messages.warning(request, f'Amount should be greater than { coupon.min_amount }')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            if coupon.is_expired:
                messages.warning(request,'Coupon expired')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except ObjectDoesNotExist:
             messages.warning(request,'Invalid Coupon.')
             return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        try:
            used_coupon = UsedCoupon.objects.get(user = request.user,coupon = coupon)
            if used_coupon.status:
                messages.warning(request,'Coupon Already Used')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                used_coupon.status = True
                used_coupon.save()
        except ObjectDoesNotExist:
            used_coupon = UsedCoupon.objects.create(user = request.user,coupon = coupon)

        coupon.used += 1
        coupon.save()
        cart.coupon = coupon
        cart.save()
        

        messages.success(request, 'Coupon applied')        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_coupon(request, cart_id):
    cart =  CartItem.objects.get(id = cart_id)
    coupon = cart.coupon
    coupon.used -= 1
    coupon.save()
    
    used_coupon = UsedCoupon.objects.get(user = request.user,coupon = coupon)
    used_coupon.status = False
    used_coupon.save()

    cart.coupon = None
    cart.save()

    messages.success(request, 'Coupon removed')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def add_address(request):
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        print(address_form.errors)
        if address_form.is_valid():
            address_line_1 = address_form.cleaned_data['address_line_1']
            address_line_2 = address_form.cleaned_data['address_line_2']
            city = address_form.cleaned_data['city']
            state = address_form.cleaned_data['state']
            country = address_form.cleaned_data['country']
            pincode = address_form.cleaned_data['pincode']
            address = UserProfile.objects.create(user = request.user, address_line_1 = address_line_1, address_line_2 = address_line_2,city = city,state=state, country = country, pincode = pincode)
    return redirect('checkout')