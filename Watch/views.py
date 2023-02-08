from django.shortcuts import render
from store.models import Product,Banner

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('-created_date')
    for pro in products:
        if pro.is_offer:
            pro.offered_price = pro.price - pro.offer
            pro.save()
    context = {
        'products': products,
        'banner':Banner.objects.all()
    }
    return render(request, 'home.html', context)