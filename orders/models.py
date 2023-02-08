from django.db import models
from accounts.models import Account
from store.models import Product, Variation
from accounts.models import UserProfile

class Payment(models.Model):
    user            = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id      = models.CharField(max_length=100)
    payment_method  = models.CharField(max_length=100)
    # this is the total amount paid
    amount_paid     = models.CharField(max_length=100)
    status          = models.CharField(max_length=100)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):

    STATUS = (
        ('Placed', u'Placed'),
        ('Delivered', u'Delivered'),
        ('Cancelled', u'Cancelled'),
        ('Returned', u'Returned')
    )

    user           = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment        = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number   = models.CharField(max_length=20)
    address = models.ForeignKey(UserProfile,null=True,on_delete=models.CASCADE)
    order_note     = models.CharField(max_length=100, blank=True)
    order_total    = models.FloatField(null=True)
    tax            = models.FloatField(null=True)
    status         = models.CharField(max_length=10, choices=STATUS, default='Placed')
    ip             = models.CharField(blank=True, max_length=20)
    is_ordered     = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

  
    def full_address(self):
        return f'{self.address.address_line_1} {self.address.address_line_2}'
    

    def __str__(self):
        return self.user.first_name


class OrderProduct(models.Model):
    order         = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment       = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user          = models.ForeignKey(Account, on_delete=models.CASCADE)
    product       = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations    = models.ManyToManyField(Variation, blank=True)
    #color and size deleted as we dont need it
    quantity      = models.IntegerField()
    product_price = models.FloatField()
    ordered       = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name