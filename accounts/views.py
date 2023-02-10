from django.shortcuts import render,redirect,get_object_or_404
from .forms import RegistrationForm,UserForm,UserProfileForm
from .models import Account,UserProfile,OTP
from orders.models import *
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage,send_mail


from cart.views import _cart_id
from cart.models import Cart, CartItem

# from mixins import MessaHandler
import random, string
from django.contrib.auth import login

import requests
import pyotp
from django.utils import timezone

from xhtml2pdf import pisa
import xlwt
from io import BytesIO
from datetime import datetime
from django.template.loader import get_template
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name        = form.cleaned_data['first_name']
            last_name         = form.cleaned_data['last_name']
            phone_number      = form.cleaned_data['phone_number']
            email             = form.cleaned_data['email']
            password          = form.cleaned_data['password']
            username          = email.split("@")[0]
            user              = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password )
            user.phone_number = phone_number
            user.save()
            
            #create user profile
            profile                 = UserProfile()
            profile.user_id         = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()
            
            #user ACTIVATION
            current_site  = get_current_site(request)
            mail_subject  = 'Please activate your account'
            message       = render_to_string('accounts/account_verification_email.html',{
                'user'  : user,
                'domain':current_site,
                'uid'   :urlsafe_base64_encode(force_bytes(user.pk)),#no one can see primary key
                'token' :default_token_generator.make_token(user),
            })
            to_email    = email
            send_email  = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            #messages.success(request, 'Thank you for Registrating with us, we have sent you an verification email,please verify' )
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form    = RegistrationForm()
    context ={
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def login_user(request):
    
    if request.method == 'POST':
        email    = request.POST['email']
        password = request.POST['password']
        
        # phone_number =request.POST.get('phone_number')
        # profile      =Profile.objects.filter(phone_number = phone_number)
        # if not profile.exists():
        #     return redirect('/register/')
        
        # profile[0].otp = random.randint(1000 , 9999)
        # profile[0].save()
        # message_handler = MessaHandler(phone_number, profile[0].otp).send_otp_on_phone()
        
        # return redirect(f'/otp/{profile[0].uid}')
            
        
        user   = auth.authenticate(email=email, password=password)
        account=Account.objects.get(email=email)
        if account.is_block:
            messages.error(request, 'User is blocked')
            return redirect('login')
        if user is not None :                                                                         #to assign guests cart to loginned user
                try:
                    
                    cart                        = Cart.objects.get(cart_id = _cart_id(request))                     
                    is_cart_item_exists         = CartItem.objects.filter(cart = cart).exists()
                
                    if is_cart_item_exists:
                        cart_item               = CartItem.objects.filter(cart=cart)
                        
                        product_variation = []
                        for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))   
                        
                        #get the cartitem from user to access his production variations
                        cart_item           = CartItem.objects.filter(user = user) #return cartitem objects
          
            
                        ex_var_list = []
                        id          = []
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id)
                                    
                        #product_variation = [1,2,3,4,5,6]
                        #ex_var_list      = [4,6,3,5]
                        
                        for pr in product_variation:
                            if pr in ex_var_list:
                                index          = ex_var_list.index(pr)
                                item_id        = id[index]
                                item           = CartItem.objects.get(id =  item_id)
                                item.quantity += 1
                                item.user      = user
                                item.save()
                            else:
                                cart_item = CartItem.objects.filter(cart = cart)
                        
                                for item in cart_item:
                                    item.user  = user
                                    item.save()        #assigning the user to cartitem
                except:
                    
                    pass
                auth.login(request, user)
                messages.success(request, 'You are now logged in.')
                url  =  request.META.get('HTTP_REFERER')                   #it will store the previous url where you came 
                try:
                    query = requests.utils.urlparse(url).query
                    print('query ->', query)#next=/cart/checkout/
                    print('--------------')
                    
                    params = dict(x.split('=') for x in query.split('&')) #it will split the  = sign and make next as key and cart/checkout as value
                    # print('params ->', params)
                    if 'next' in params:
                        nextpage = params['next']
                        return redirect(nextpage)
                        
                except:
                    return redirect('home')
                    
           
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')


def otp_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            if Account.objects.filter(email__iexact=request.POST['email']).exists():
                email=request.POST['email']
                print(email)
                user = Account.objects.filter(email=email).first()
                otp  = generate_otp()
                print(otp)
                expiration_time = timezone.now() + timezone.timedelta(minutes=5)
                print(user)
                #print(OTP.objects.create(otp=otp, expiration_time=expiration_time, user=user))
                OTP.objects.create(otp=otp, expiration_time=expiration_time, user=user)
                try:
                    send_mail(
                    'OTP for Signup Verification',
                    'Your OTP is {}. It will expire in 3 minutes.'.format(otp),
                    'mithuncy65@gmail.com',
                    [user.email],
                    fail_silently=False,
                    )
                    return redirect('verify_otp')
                except:
                    messages.error(request,"OTP send failed")
            else:
                messages.error(request,"Invalid email")
    return render(request, 'accounts/otp_login.html')

def verify_otp(request):
    if request.user.is_authenticated: 
         return redirect('home')
    else:
        if request.method == 'POST':
            otp = request.POST.get('otp')
            print(otp)
            try:
                otp_obj = OTP.objects.get(otp=otp, expiration_time__gt=timezone.now())
                user    = otp_obj.user
                print(user)
      
    
                login(request, user)
                return redirect('home') 
            except OTP.DoesNotExist:
                return render(request, "accounts/verify_otp.html", {'error': 'Invalid or expired OTP'})
    return render(request, "accounts/verify_otp.html")


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))



@login_required(login_url = 'login' )
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.' )
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user= Account._default_manager.get(pk=uid)
    except(TypeError,ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
    
@login_required(login_url = 'login')
def dashboard(request):
    orders       = Order.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered=True)
    orders_count = orders.count()
    #userprofile  = UserProfile.objects.filter(user_id = request.user.id)
    context = {
        'orders_count': orders_count,
        
    }
    return render(request, 'accounts/dashboard.html', context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            
            
            #Reset Password email
            current_site  = get_current_site(request)
            mail_subject  = 'Reset your Password'
            message       = render_to_string('accounts/reset_password_email.html',{
                'user'  : user,
                'domain':current_site,
                'uid'   :urlsafe_base64_encode(force_bytes(user.pk)),#no one can see primary key
                'token' :default_token_generator.make_token(user),
            })
            to_email    = email
            send_email  = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            
            messages.success(request, 'Password reset email has been sent to your email address')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid  = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):#if the check token returns true i.e. if it has the token
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')
    
def resetPassword(request):
    if request.method == 'POST':
        password         = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid  = request.session.get('uid')
            user = Account.objects.get(pk = uid)
            user.set_password(password)#this setpassword will take the password and hash it
            user.save()
            messages.success(request, 'Password reset successfull')
            return redirect('login')
        
            
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
        
    else:
        return render(request, 'accounts/resetPassword.html')
    
@login_required(login_url='login')   
def my_orders(request):
    orders = Order.objects.filter(user = request.user, is_ordered = True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)  #orderproduct referred here in models
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    # #coupon = CouponDetail.objects.filter(user=request.user)
    # for i in coupon:
    #     coupon=i
    context = {
        'order_detail': order_detail,
        'order': order,
    #     'subtotal': subtotal,
    #     #'coupon':coupon,
     }
    return render(request, 'accounts/order_detail.html', context)

@login_required(login_url='login')
def edit_profile(request):
        #userprofile = get_object_or_404(UserProfile, user=request.user)
        if request.method == 'POST':
            user_form = UserForm(request.POST, instance=request.user)
            # profile_form = UserProfileForm(
            #     request.POST, request.FILES, instance=userprofile)
            if user_form.is_valid() :
                user_form.save()
                # profile_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('edit_profile')
        else:
            user_form = UserForm(instance=request.user)
            # profile_form = UserProfileForm(instance=userprofile)
        context = {
            'user_form': user_form,
            # 'profile_form': profile_form,
            'userprofile': user_form,
        }
        return render(request, 'accounts/edit_profile.html', context)
@login_required(login_url='login')   
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password     = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        user = Account.objects.get(username__exact=request.user.username) #in models.py create_user method has username  iexact is case insensitive but exact is exactly ith shouldbe
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request) #by default django will log you out
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')
def order_history(request):
    order = Order.objects.all().order_by('-created_at')
    context={
        'order':order,
    }
    return render(request,'order_de.html',context)
def sales_report(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        order = Order.objects.all()
        print(start_date)
        
        if start_date and end_date:
            print(start_date)
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            order = order.order_by('-created_at').filter(created_at__range=[start_date, end_date])
        else:
            order = Order.objects.all().order_by('-created_at')
        now=datetime.today()
        data={
            'orders': order,
    }
        response = HttpResponse(content_type='application/pdf')
        filename = "Report"+str(now)+ ".pdf"
        content = "attachment; filename="+filename
        response['Content-Disposition'] = content
        template = get_template("order_de.html")
        html = template.render(data)
        result = BytesIO()
        pdf = pisa.pisaDocument( BytesIO(html.encode("ISO-8859-1")), result)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf')
        return response
    else:
        return redirect('order_detail')