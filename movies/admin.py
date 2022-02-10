from django.contrib import admin

# Register your models here.
from .models import Genre, Persona, Rating, UserProfile
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

class PersonaAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'created_at', 'updated_at')

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    prepopulated_fields = {"slug": ("name",)}
    #TODO: make slugs readonly or hide them from the UI
    # readonly_fields = ('slug',)
    # exclude=('slug',)

class RatingAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'rating', 'created_at', 'updated_at')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')



# ------------------
# Model Registration
# ------------------   
admin.site.register(Movie, MovieAdmin)
admin.site.register(Persona, PersonaAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
