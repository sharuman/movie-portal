from django.contrib import admin

# Register your models here.
from .models import Persona
from .models import Movie

admin.site.register(Movie)
admin.site.register(Persona)
