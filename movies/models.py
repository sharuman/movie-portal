from django.db import models

# Create your models here.

class Persona(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    @property
    def full_name(self):
        "Returns the persona's full name."
        return '%s %s' % (self.first_name, self.last_name)

class Movie(models.Model):
    title = models.CharField(max_length=255)
    title_original = models.CharField(max_length=255)

    class MovieFormat(models.TextChoices):
        COLOR = 'color',
        BLACK_AND_WHITE = 'b/n'

    format = models.CharField(
        max_length=5,
        choices=MovieFormat.choices,
        default=MovieFormat.COLOR
    )
    slug = models.CharField(max_length=255, primary_key=True)
    running_time = models.IntegerField()
    trailer = models.TextField()
    plot = models.TextField()
    released_on = models.DateField()
    created_at = models.DateTimeField()

    director = models.ManyToManyField(
        Persona,
        related_name='movie_directors',
    )
    actors = models.ManyToManyField(
        Persona,
        related_name='movie_actors'
    )

    class Meta:
        ordering = ["title"]

    # TODO: Can this work not only with movies?
    # If yes, it should be implemented in a separate Django app (module)
    def related_movies(self):
        pass
