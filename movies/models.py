from random import choices
from turtle import update
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

# Create your models here.

class Persona(models.Model):
    
    # Persona is representative of both, actors/actresses and directors
    
    TYPE_CHOICES = (
        (0, 'Director'),
        (1, 'Actor'),
    )

    full_name = models.CharField(max_length=200)
    type = models.IntegerField(choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Genre(models.Model):
    
    # Genre is representative of the type of the movie
    
    name = models.CharField(max_length=200, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    g_slug = models.SlugField(max_length=254, unique=True)

    def __str__(self):
       return self.name    


class Movie(models.Model):

    # Represents all the movie details

    title = models.CharField(max_length=300)
    m_slug = models.SlugField(max_length=254, unique=True)
    length = models.FloatField()
    viewer_rating = models.ManyToManyField(User, through='Rating', blank=True)
    released_on = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    director = models.ManyToManyField(Persona, related_name='movie_director')
    actor = models.ManyToManyField(Persona, related_name='movie_actor')
    genre = models.ManyToManyField(Genre, related_name='movie_genre')
    trailer = models.URLField(max_length=500, blank=True, default=None)
    plot = models.TextField()

    
    class Meta:
        ordering = ["title"]
    
    def __str__(self):
       return self.title
   
class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    star_rating = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],)

