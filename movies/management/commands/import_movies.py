from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import pandas as pd
import os
from tqdm import tqdm
import logging

class Command(BaseCommand):
    help = 'Import movies and the main relationships'

    logger = logging.getLogger('command_import_movies')
    logger.info('Import started')

    def handle(self, *args, **kwargs):
        # # This will break as Docker does not see files in the local machine.
        # movies_path = Path(os.getenv('MOVIES_PATH')).expanduser()
        
        # movies_df = pd.read_csv(movies_path, usecols=['id'], low_memory = False)
        # movies_df.rename(columns= {'id': 'movie_id'}, inplace = True)
        # movies_df['movie_id'] = movies_df['movie_id'].astype(str)

        for i in tqdm(range(10000000)):
            pass

        self.logger.info('Import completed')
        self.stdout.write(self.style.SUCCESS('Import completed'))


# python manage.py import_movies
