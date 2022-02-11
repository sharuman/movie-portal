from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import pandas as pd
import os
from tqdm import tqdm
import urllib.request
import logging
import requests
from movies.models import Movie
from datetime import datetime
from django.conf import settings

class Command(BaseCommand):
    help = 'Get movie posters from the TMDB API and save them locally'

    logger = logging.getLogger('command_get_movie_posters')
    logger.info('Import started')

    def handle(self, *args, **kwargs):
        movies_path = Path(os.getenv('MOVIES_PATH')).expanduser()
        base_path = '.'
        posters_path = os.path.join(base_path, 'static/images/posters/')
        os.makedirs(os.path.dirname(posters_path), exist_ok=True)

        movies = pd.read_csv(movies_path, usecols=['id'], low_memory = False)
        movies.rename(columns= {'id': 'movie_id'}, inplace = True)
        movies['movie_id'] = movies['movie_id'].astype(str)

        # List of movie ids for which we already have a poster
        movies_with_poster: list(str) = [filename[:-4] for filename in os.listdir(posters_path) if filename.endswith('.jpg')]
        movies_without_poster_df = movies[~movies['movie_id'].isin(movies_with_poster)]
        self.logger.info('{} movies already have a poster'.format(len(movies_with_poster)))
        self.logger.info('I will download posters for the remaining {} movies'.format(len(movies_without_poster_df)))
        
        # Register `pandas.progress_apply` and `pandas.Series.map_apply` with `tqdm`
        # (can use `tqdm.gui.tqdm`, `tqdm.notebook.tqdm`, optional kwargs, etc.)
        tqdm.pandas(desc="Saving posters")
        movies_without_poster_df.progress_apply(lambda row: self.getImage(row['movie_id'], posters_path), axis=1)
       
        self.logger.info('Import completed')
        self.stdout.write(self.style.SUCCESS('Import completed'))

    def getImage(self, movie_id, output_path):
        try:
            url = self.getPosterUrl(movie_id)
            filename = '{}.jpg'.format(movie_id)
            image_path = os.path.join(output_path, filename)
            urllib.request.urlretrieve(url, image_path)

            movie = Movie.objects.get(id=int(movie_id))
            movie.poster_path = image_path
            movie.updated_at = datetime.now()
            movie.save()
        except Movie.DoesNotExist:
            self.logger.warn('I am not able to set the poster filename: movie {} has not been found in the database'.format(str(movie_id)))
        except Exception as e:
            self.logger.warn(e)
           
    def getPosterUrl(self, movie_id: int) -> str:
        """Get poster image url
        Args:
            movie_id (int): id of movie for which poster is needed.

        Returns:
            str: movie poster url
        """
        api_key = os.getenv('TMDB_API_KEY')
        try:
            url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(movie_id, api_key)
            data = requests.get(url)
            data = data.json()
            poster_path = data['poster_path']
            full_path = "https://image.tmdb.org/t/p/w300/" + poster_path

            return full_path
        except Exception:
            msg = 'Error while getting poster for movie id ' + str(movie_id)
            movie = Movie.objects.get(id=int(movie_id))
            image_path = os.path.join(settings.POSTERS_PATH, 'poster_placeholder.png')
            movie.poster_path = image_path
            movie.updated_at = datetime.now()
            movie.save()
            # We want to log the message when importing posters
            raise Exception(msg)

# python manage.py get_movie_posters
