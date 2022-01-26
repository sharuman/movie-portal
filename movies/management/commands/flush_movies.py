from django.core.management.base import BaseCommand, CommandError
from movies.models import Genre, Movie, Persona

class Command(BaseCommand):
    help = 'Flush movies and related tables'

    #TODO: add user path and more error handling later
    def handle(self, *args, **kwargs):
        flush_movies(self)

# python manage.py flush_movies
def flush_movies(command):
    command.stdout.write(command.style.NOTICE('Flush started'))

    Movie.objects.all().delete()
    Genre.objects.all().delete()
    Persona.objects.all().delete()

    command.stdout.write(command.style.SUCCESS('Flush completed'))