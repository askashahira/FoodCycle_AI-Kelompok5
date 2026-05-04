from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}), 
        required=False,
        label='Alamat'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'address']

class ProfileEditForm(forms.ModelForm):
    latitude = forms.DecimalField(
        max_digits=10, decimal_places=8, 
        required=False, 
        widget=forms.HiddenInput()
    )
    longitude = forms.DecimalField(
        max_digits=11, decimal_places=8, 
        required=False,
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'address', 'latitude', 'longitude']
        labels = {
            'username': 'Username',
            'email': 'Email',
            'address': 'Alamat',
        }
