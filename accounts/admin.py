from django.contrib import admin
from .models import Account,UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
# Register your models here.

class AccountAdmin(BaseUserAdmin):
    #model        = Account
    list_display      = ('email', 'username', 'phone_number', 'date_joined', 'last_login', 'is_active', 'is_block')
    filter_horizontal = ()
    list_filter       = ()
    fieldsets = ()
    ordering          = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined')
    
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img sr"{}" width = "30" style="border-radius:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')
admin.site.register(Account,AccountAdmin )
admin.site.register(UserProfile, UserProfileAdmin)
