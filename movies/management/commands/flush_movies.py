from django.core.management.base import BaseCommand, CommandError
from movies.models import Genre, Movie, Persona

class Command(BaseCommand):
    help = 'Flush movies and related tables'

    #TODO: add user path and more error handling later
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Flush started'))

        Movie.objects.all().delete()
        Genre.objects.all().delete()
        Persona.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Flush completed'))

# python manage.py flush_movies
