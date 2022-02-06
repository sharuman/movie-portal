from django.db.models import Avg
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

# -------------
# PERSONA MODEL
# -------------
# Persona represents both, actors/actresses and directors
class Persona(models.Model):    
    full_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Needed to display Persona name in the drop-down list when setting movie-persona 
    # relationships in the backoffice 
    def __str__(self):
       return self.full_name  

# -----------
# GENRE MODEL
# -----------
class Genre(models.Model):
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Needed to display Genre name in the drop-down list when setting movie-genre 
    # relationships in the backoffice     
    def __str__(self):
       return self.name    

# -----------
# MOVIE MODEL
# -----------
class Movie(models.Model):
    title = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, unique=True)
    length = models.FloatField(default=0.0, blank=True, null=True)
    released_on = models.DateField(blank=True, null=True)
    trailer = models.URLField(max_length=254, blank=True, null=True)
    plot = models.TextField(blank=True, null=True)
    # Relationships
    directors = models.ManyToManyField(Persona, related_name='directors')
    actors = models.ManyToManyField(Persona, related_name='actors')
    genres = models.ManyToManyField(Genre, related_name='genres')
    ratings = models.ManyToManyField(User, through='Rating', blank=True)
    # Posters can be treated as assets, therefore we could create an Assets model and
    # use https://django-polymorphic.readthedocs.io/en/stable/quickstart.html
    poster_path = models.URLField(max_length=254, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Needed to display Movie title in the Ratings section of the backoffice   
    def __str__(self):
       return self.title

    def get_actors(self):
        actors = self.actors.values_list('full_name', flat=True)[:5]
        return ', '.join(actors)

    def get_directors(self):
        directors = self.directors.values_list('full_name', flat=True)[:5]
        return ', '.join(directors)

    def get_genres(self):
        genres = self.genres.values_list('name', flat=True)[:5]
        return ', '.join(genres)
    
    def get_avg_ratings(self):
        avg_ratings = self.ratings.values('rating__rating').aggregate(avg_rating=Avg('rating__rating'))['avg_rating']
        return avg_ratings

# ------------
# RATING MODEL
# ------------  
class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # A user can rate a movie only once
        unique_together = (('movie', 'user'))
