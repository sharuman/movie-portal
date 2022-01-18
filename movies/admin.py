from django.contrib import admin

# Register your models here.
from .models import Genre, Persona, Rating
from .models import Movie

class MovieAdmin(admin.ModelAdmin):
    prepopulated_fields = {"m_slug": ("title",)}

class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {"g_slug": ("name",)}

admin.site.register(Movie, MovieAdmin)
admin.site.register(Persona)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Rating)
