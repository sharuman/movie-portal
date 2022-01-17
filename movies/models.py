from random import choices
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Persona(models.Model):
    
    # Persona is representative of both, actors/actresses and directors
    
    TYPE_CHOICES = (
        (0, 'Both'),
        (1, 'Actor'),
        (2, 'Director'),
    )

    full_name = models.CharField(max_length=200, primary_key=True)
    type = models.IntegerField(choices=TYPE_CHOICES)

class Genre(models.Model):
    
    # Genre is representative of the type of the movie
    
    name = models.CharField(max_length=200, primary_key=True)    

class Viewer(models.Model):
    
    # User is representative of information of users who interact with the website
    
    full_name = models.CharField(max_length=300, primary_key=True)

class Movie(models.Model):

    # Represents all the movie details

    title = models.CharField(max_length=300, primary_key=True)
    length = models.FloatField()
    star_rating = models.ManyToManyField(Viewer, related_name='assigned_by', blank=True)
    released_on = models.DateField()
    added_on = models.DateTimeField(auto_now_add=True)
    director = models.ManyToManyField(Persona, related_name='movie_director')
    actor = models.ManyToManyField(Persona, related_name='movie_actor')
    genre = models.ManyToManyField(Genre, related_name='movie_genre')
    trailer = models.URLField(max_length=500, blank=True, default=None)
    plot = models.TextField()

    
    # class Meta:
    #     ordering = ["title"]
    # format = models.CharField(
    #     max_length=5,
    #     choices=MovieFormat.choices,
    #     default=MovieFormat.COLOR
    # )
   

