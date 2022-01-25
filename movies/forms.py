from cProfile import label
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control'}),
        label='Full name'
    )

    username = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}),
        label='Username'
    )

    email = forms.EmailField(
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
        label="Confirmation password",
    )

    class Meta:
        # built-in User model
        model = User
        fields = ['full_name', 'username', 'email',
                  'password1', 'password2']
