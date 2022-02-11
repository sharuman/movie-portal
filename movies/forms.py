from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms

from .models import UserProfile

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

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}),
        label='First name'
    )

    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}),
        label='Last name'
    )

    username = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}),
        label='Username'
    )

    email = forms.EmailField(
        max_length=50,
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'E-mail Address', 'class': 'form-control'}),
        label='E-mail'
    )

    password1 = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}),
        label="Password"
    )

    password2 = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Entered Password', 'class': 'form-control'}),
        label="Confirmation password"
    )

    USERNAME_FIELD = 'email'

    class Meta:
        # built-in User model
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    biography = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    fav_genre = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    class Meta:
        model = UserProfile
        fields = ['image', 'biography']

