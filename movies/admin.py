from django.contrib import admin

# Register your models here.
from .models import Genre, Persona, Viewer
from .models import Movie

admin.site.register(Movie)
admin.site.register(Persona)
admin.site.register(Viewer)
admin.site.register(Genre)
