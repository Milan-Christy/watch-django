from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
import uuid

# Create your models here.
#for superadmin
class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):       #for creating normal user
        if not email:
            raise ValueError('User must have an email address')

        if not username:
            raise ValueError('User must have an username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):             #for creating superuser
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin      = True
        user.is_active     = True
        user.is_staff      = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

#for custom user
class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    username  = models.CharField(max_length=50, unique=True)
    email  = models.EmailField(max_length=100, unique=True)
    phone_number  = models.CharField(max_length=50)
    is_block      = models.BooleanField(default=False)
    
    
    #required as these are mandatory for creating custom user model
    
    date_joined   = models.DateTimeField(auto_now_add=True)
    last_login    = models.DateTimeField(auto_now_add=True)
    is_admin      = models.BooleanField(default=False)
    is_staff      = models.BooleanField(default=False)
    is_active     = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    objects = MyAccountManager()      #we need to tell Account that we are using myaccmanager
    
    def __str__(self):
        return self.email       #this is to when we return account object we should return email to template
    
    def has_perm(self, perm, obj=None):
        return self.is_admin    #this is for if the user is admin he has all the permissions to do everything
    
    def has_module_perms(self, add_label):
        return True
    
    def get_all_permissions(user=None):
        if user.is_superadmin:
            return set()
        
class UserProfile(models.Model):
    user            = models.ForeignKey(Account, on_delete=models.CASCADE) #we want to have only one profile for one person  reason for one-one field
    address_line_1  = models.CharField(blank=True, max_length=100)
    address_line_2  = models.CharField(blank=True, max_length=100)
    # profile_picture = models.ImageField(blank=True, upload_to='userprofile')#inside media folder profilepic is created
    city            = models.CharField(blank=True, max_length=20)
    state           = models.CharField(blank=True, max_length=20)
    country         = models.CharField(blank=True, max_length=20)
    pincode         = models.IntegerField(blank=True,default=None,null=True,)

    def __str__(self):
        return self.user.first_name

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
  
class OTP(models.Model):
    otp             = models.CharField(max_length=6)
    expiration_time = models.DateTimeField()
    user            = models.ForeignKey(Account, on_delete=models.CASCADE)
