from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    password           = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Enter Password','minlength':8,'maxlength':16,
        #'class' : 'form_control',
    }))
    
    confirm_password   = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Confirm Password'
    }))
    
    class Meta:
        model          = Account
        fields         = ['first_name','last_name','phone_number','email','password']
    
    # to add formcontrol commonly for all fields, to design ,it will lookthrough all the fields and assign formcontrol to all
        
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder']   = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder']    = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder']        = 'Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
    def clean(self):
        cleaned_data         = super(RegistrationForm, self).clean()
        password             = cleaned_data.get('password')
        confirm_password     = cleaned_data.get('confirm_password')
        
        # if password < '8':
        #      raise forms.ValidationError(
        #         "Password contain atleast 8 character"
        #     ) 
        
        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match"
            )