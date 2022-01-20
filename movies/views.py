from contextlib import redirect_stdout
from multiprocessing import AuthenticationError
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
import datetime
from django.views import View

# importing needed, created forms from forms.py
from .forms import SignUpForm

# Create your views here.


def index(request):
    now = datetime.datetime.now()
    return render(request, 'index.html', {'now': now})

# def home(request):
#     return render(request, 'home.html')


class SignUpView(View):

    form_class = SignUpForm
    initial = {'key': 'value'}
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()        
            return redirect(to='/')
    
        else:
            return render(request, self.template_name, {'form': form})
