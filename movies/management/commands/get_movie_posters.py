from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import pandas as pd
import os
from tqdm import tqdm
import urllib.request
import logging
import requests

class Command(BaseCommand):
    help = 'Save movie posters locally'

    def handle(self, *args, **kwargs):
        movies_path = Path(os.getenv('MOVIES_PATH')).expanduser()
        base_path = '.'
        posters_path = os.path.join(base_path, 'assets/posters/')
        os.makedirs(os.path.dirname(posters_path), exist_ok=True)

        movies_df = pd.read_csv(movies_path, usecols=['id'], low_memory = False)
        movies_df.rename(columns= {'id': 'movie_id'}, inplace = True)
        movies_df['movie_id'] = movies_df['movie_id'].astype(str)

        # List of movie ids for which we already have a poster
        movies_with_poster: list(str) = [filename[:-4] for filename in os.listdir(posters_path) if filename.endswith('.jpg')]
        movies_without_poster_df = movies_df[~movies_df['movie_id'].isin(movies_with_poster)]

        # Register `pandas.progress_apply` and `pandas.Series.map_apply` with `tqdm`
        # (can use `tqdm.gui.tqdm`, `tqdm.notebook.tqdm`, optional kwargs, etc.)
        tqdm.pandas(desc="Saving posters")
        movies_without_poster_df.progress_apply(lambda row: self.getImage(row['movie_id'], posters_path), axis=1)
       
        self.stdout.write(self.style.SUCCESS('Import completed'))

    def getImage(self, movie_id, output_path):
        try:
            url = self.getPosterUrl(movie_id, True)
            image_path = os.path.join(output_path, '{}.jpg'.format(movie_id))
            urllib.request.urlretrieve(url, image_path)
        except Exception as e:
            print(e)

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
            # We want to log the message when importing posters
            raise Exception(msg)

# python manage.py get_movie_posters
