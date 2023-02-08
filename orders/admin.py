from django.contrib import admin
from .models import Payment, Order, OrderProduct

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0 #otherwise django shows 3 extra rows we dont need it

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'order_total', 'tax', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    list_editable = ['status']
    fields =['status',]
    search_fields = ['order_number', 'last_name', 'phone', 'email']
    list_per_page = 10
    inlines = [OrderProductInline]
    
# class PaymentAdmin(admin.ModelAdmin):
#     list_display= ['user', 'payment_id', 'payment_method', 'amount_paid', 'status', 'created_at', ]
#     search_fields= ['payment_id', 'payment_method', 'status',]
    
admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
