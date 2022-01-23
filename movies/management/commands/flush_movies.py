from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from pathlib import Path
import pandas as pd
import os
from tqdm import tqdm
import logging
from slugify import slugify
import itertools

from movies.models import Genre, Movie, Persona

#TODO: Discuss, how and when logger should be used
logger = logging.getLogger('command_flush_movies')

class Command(BaseCommand):

    help = 'Flush movies and related tables'

    def handle(self, *args, **kwargs):
        # # This will break as Docker does not see files in the local machine.
        #TODO: add user path and more error handling later

        # movies_path = Path(os.getenv('MOVIES_PATH')).expanduser()

        logger.info('Flush started')

        self.flush_movies()

        logger.info('Flush completed')
        self.stdout.write(self.style.SUCCESS('Flush completed'))

    #Flushes filled Movie database, keeps users
    def flush_movies(self)->None:
        Movie.objects.all().delete()
        Genre.objects.all().delete()
        Persona.objects.all().delete()


# python manage.py import_movies



