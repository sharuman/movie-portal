from django.core.management.base import BaseCommand, CommandError
import os
from tqdm import tqdm
import logging
import requests
from movies.models import Movie
from datetime import datetime

class Command(BaseCommand):
    help = 'Get movies trailer from the TMDB API and save them on the db'
    logger = logging.getLogger('command_set_movies_trailer')

    def handle(self, *args, **kwargs):
        ids = Movie.objects.filter(trailer__isnull=True).values_list('id', flat=True)
        
        if not ids:
            self.stdout.write(self.style.WARNING('Nothing to do: no movie found in the database'))
        else:
            self.logger.info('Import started')
            with tqdm(total=len(ids)) as bar:
                for id in ids.iterator():
                    self.getTrailerUrl(id)
                    bar.update(1)
        
            self.logger.info('Import completed')
            self.stdout.write(self.style.SUCCESS('Import completed'))


    def getTrailerUrl(self, movie_id: int) -> str:
        """Get trailer url
        Args:
            movie_id (int): id of movie for which the trailer url is needed.

        Returns:
            str: movie trailer url
        """
        api_key = os.getenv('TMDB_API_KEY')
        try:
            url = "https://api.themoviedb.org/3/movie/{}/videos?api_key={}&language=en-US".format(movie_id, api_key)
            data = requests.get(url)
            data = data.json()
            video_id = data['results'][0]['key']
            trailer_url = 'https://www.youtube.com/embed/{}'.format(video_id)

            movie = Movie.objects.get(id=movie_id)
            movie.trailer = trailer_url
            movie.updated_at = datetime.now()
            movie.save()
        except IndexError:
            self.logger.warn('Movie id {} does not have a trailer'.format(movie_id))
        except Exception as e:
            print(e)
            self.logger.error('Error while getting trailer for movie id {}'.format(movie_id))

# python manage.py set_movies_trailer
