from django.db import models
from store.models import Product,Variation
from accounts.models import Account
# Create your models here.
class Coupon(models.Model):
    code       = models.CharField(max_length=50, unique=True)
    is_expired = models.BooleanField(default =False)
    amount     = models.IntegerField(default=10)
    min_amount = models.IntegerField(default=500)
    max_use    = models.IntegerField(default=100)
    used       = models.IntegerField(default=0)
    created    = models.DateTimeField(auto_now_add=True)
    updated    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.code)

class UsedCoupon(models.Model):
    user   = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True, related_name="used_coupons")
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, blank=True, null=True, related_name="used_coupons")
    status = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user.username)
# Create your models here.
class Cart(models.Model):
    cart_id    = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.cart_id
class CartItem(models.Model):
    user        = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product     = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations  = models.ManyToManyField(Variation, blank=True)
    cart        = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True,related_name="items")
    quantity    = models.IntegerField()
    is_active   = models.BooleanField(default=True)
    coupon      = models.ForeignKey(Coupon, on_delete=models.SET_NULL,null=True,blank=True) 
    
    def sub_total(self):
        if self.product.is_offer:
            return self.product.offered_price * self.quantity
        else:
            return self.product.price * self.quantity
            
    
    def get_cart_total(self):
        #items = self.items.all()
        price = []

        #for cart_item in self.items:
        price.append(self.product.price * self.quantity)

        if self.coupon:
            if self.coupon.min_amount < sum(price):
                return sum(price) - self.coupon.amount
        
        return sum(price)
    
    def __unicode__(self):
        return self.product
    
