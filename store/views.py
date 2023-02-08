from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,ReviewRating,ProductGallery
from category.models import Category
from cart.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger,Paginator
from cart.models import CartItem
from django.http import HttpResponse
from django.db.models import Q
from .forms import ReviewForm

from orders.models import OrderProduct


from django.contrib import messages
# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None
    prod=None
    price_min = request.GET.get('price_min')
    print(price_min)
    price_max = request.GET.get('price_max')
    print(price_max)
    if category_slug != None:
        categories    = get_object_or_404(Category, slug=category_slug)
        products      = Product.objects.filter(category=categories, is_available=True)
        paginator     = Paginator(products, 1)
        page          = request.GET.get('page')
        paged_products= paginator.get_page(page)
        product_count = products.count()
    else:
        products      = Product.objects.all().filter(is_available=True).order_by('id')
        paginator     = Paginator(products, 2)
        page          = request.GET.get('page')
        paged_products= paginator.get_page(page)
        product_count = products.count()
    products = Product.objects.all().filter(is_available=True)
    if price_min:
        prod = products.filter(price__gte=price_min)
        product_count = prod.count()
        print(product_count)
    if price_max:
        prod = products.filter(price__lte=price_max)
        product_count = prod.count()
        print(product_count)
    
    context = {
        
        'prod':prod,
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart        = CartItem.objects.filter(cart__cart_id=_cart_id(request), product = single_product).exists()
        product        = Product.objects.get(slug=product_slug)

        
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
            
    else:
        orderproduct = None
        
    #get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    
    #to get the product gallery
    product_gallery =ProductGallery.objects.filter(product_id = single_product.id)
        
    
    product_gallery = ProductGallery.objects.filter(product_id=single_product)
    context ={
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct' : orderproduct,
        'reviews':reviews,
        'product_gallery':product_gallery,
    }
    return render(request, 'store/product_detail.html', context)



def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products'    :products,
        'product_count' :product_count,
    } 
    return render(request, 'store/store.html', context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')   #the previous url of the browser will get stored in url
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(user__id = request.user.id, product__id = product_id)
            form   = ReviewForm(request.POST, instance=review)        #this request.POST has all the data passed  ,instance = review is used if there is a review from theses user we need to update that not create another our form will understand that update the record 
            form.save()
            messages.success(request, 'Thank you!Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip     = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
            
            

