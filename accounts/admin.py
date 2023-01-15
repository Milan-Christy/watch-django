from django.contrib import admin
from .models import Account
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.

class AccountAdmin(BaseUserAdmin):
    #model        = Account
    list_display      = ('email', 'username', 'phone_number', 'date_joined', 'last_login', 'is_active', 'is_block')
    filter_horizontal = ()
    list_filter       = ()
    fieldsets = ()
    ordering          = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined')
admin.site.register(Account,AccountAdmin )

