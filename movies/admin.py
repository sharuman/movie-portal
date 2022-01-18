from django.contrib import admin

# Register your models here.
from .models import Genre, Persona, Rating
from .models import Movie

# ----------------
# Model Definition
# ----------------
class MovieAdmin(admin.ModelAdmin):
    # ManyToManyField fields aren’t supported 
    list_display = ('title', 'slug', 'length', 'released_on', 'created_at', 'updated_at')
    prepopulated_fields = {"slug": ("title",)}
    #TODO: make slugs readonly or hide them from the UI
    # readonly_fields = ('slug',)
    # exclude=('slug',)

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    prepopulated_fields = {"slug": ("name",)}
    #TODO: make slugs readonly or hide them from the UI
    # readonly_fields = ('slug',)
    # exclude=('slug',)

class RatingAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'rating', 'created_at', 'updated_at')

# ------------------
# Model Registration
# ------------------   
admin.site.register(Movie, MovieAdmin)
admin.site.register(Persona)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Rating, RatingAdmin)
