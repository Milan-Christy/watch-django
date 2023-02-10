from django.contrib import admin
from .models import Account,UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.contrib.auth.models import Group

# Register your models here.

class AccountAdmin(BaseUserAdmin):
    #model        = Account
    list_display      = ('email', 'username', 'phone_number', 'date_joined', 'last_login', 'is_active', 'is_block')
    filter_horizontal = ()
    list_filter       = ()
    fieldsets         = ()
    ordering          = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined','email', 'phone_number','first_name','last_name','password','username')
    
class UserProfileAdmin(admin.ModelAdmin):
    # def thumbnail(self, object):
    #     return format_html('<img src = "{}" width = "30" style="border-radius:50%;">'.format(object.profile_picture.url))
    # thumbnail.short_description = 'Profile Picture'
    list_display = ( 'user', 'city', 'state', 'country')
    readonly_fields = ( 'user', 'city', 'state', 'country','address_line_1','address_line_2')
admin.site.register(Account,AccountAdmin )
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.unregister(Group)