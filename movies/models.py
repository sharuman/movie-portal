from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Persona(models.Model):
    
    # Persona is representative of both, actors/actresses and directors
    
    full_name = models.CharField(max_length=200)
    

class Movie(models.Model):

    # Represents all the movie details

    movie_title = models.CharField(max_length=300)
    movie_length = models.FloatField()
    movie_genre = models.CharField(max_length=300)
    star_rating = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], blank=True)
    released_on = models.DateField()
    added_on = models.DateTimeField(auto_now_add=True)
    director = models.ManyToManyField(Persona, related_name='movie_director')
    actor = models.ManyToManyField(Persona, related_name='movie_actor')
    movie_trailer = models.URLField(max_length=500, blank=True, default=None)
    movie_plot = models.TextField()

    
    # class Meta:
    #     ordering = ["title"]
    # format = models.CharField(
    #     max_length=5,
    #     choices=MovieFormat.choices,
    #     default=MovieFormat.COLOR
    # )
   

