from cProfile import label
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms


class SignUpForm(UserCreationForm):

    # only stated fields would be used

    full_name = forms.CharField(max_length=200, required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control',
                                                              }))

    username = forms.CharField(max_length=50, required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control',
                                                             }))

    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={'placeholder': 'E-mail Address', 'class': 'form-control',
                                                           }))

    password1 = forms.CharField(max_length=50, required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control',
                                                                 }))

    password2 = forms.CharField(max_length=50,
                                            required=True,
                                            widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Entered Password',
                                                                              'class': 'form-control',
                                                                              }))
    
    class Meta:
        # built-in User model
        model = User
        fields = ['full_name', 'username', 'email',
                  'password1', 'password2']

    