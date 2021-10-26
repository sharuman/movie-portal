from django.db import models

# Create your models here.
class Movie(models.Model):
    title = models.CharField(max_length=255)
    title_original = models.CharField(max_length=255)
    format = models.TextChoices(
        '65mm',
        '75mm',
        '35mm'
    )
    slug = models.CharField(max_length=255, primary_key=True)
    running_time = models.IntegerField()
    trailer = models.TextField()
    plot = models.TextField()
    released_on = models.DateField()
    created_at = models.DateTimeField()
