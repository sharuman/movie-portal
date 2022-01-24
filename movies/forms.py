from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django import forms

class LoginForm(AuthenticationForm):

    username =  username = forms.CharField(max_length=50, required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control',
                                                             }))
    password =  forms.CharField(max_length=50, required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control',
                                                                 }))

    class Meta:
        
        # built-in User model
        model = User
        fields = ['username', 'password']
