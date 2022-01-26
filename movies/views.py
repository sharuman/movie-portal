from django.shortcuts import render, redirect
import datetime
from django.views import View

# Create your views here.
# importing needed, created forms from forms.py
from .forms import SignUpForm

def index(request):
    now = datetime.datetime.now()
    return render(request, 'index.html', {'now': now})

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
