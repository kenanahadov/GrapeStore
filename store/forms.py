from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Address,PaymentMethod
class RegisterForm(UserCreationForm):
    email=forms.EmailField(required=True)
    class Meta:
        model=User
        fields=('username','email','password1','password2')
class AddressForm(forms.ModelForm):
    class Meta:
        model=Address
        exclude=('user',)
        widgets={f:forms.TextInput(attrs={'class':'form-control'}) for f in ['full_name','line1','line2','city','state','postal_code','country']}
class PaymentForm(forms.ModelForm):
    class Meta:
        model=PaymentMethod
        exclude=('user',)
        widgets={'brand':forms.Select(attrs={'class':'form-select'}),'last4':forms.TextInput(attrs={'class':'form-control','maxlength':4})}
