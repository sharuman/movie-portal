from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from pathlib import Path
import pandas as pd
import os
from tqdm import tqdm
import logging
from slugify import slugify
import itertools
from django.conf import settings

from movies.management.commands.flush_movies import flush_movies
from movies.models import Genre, Movie, Persona


# TODO: Discuss, how and when logger should be used
logger = logging.getLogger('command_import_movies')

class Command(BaseCommand):
    help = 'Import movies and the main relationships'

    def add_arguments(self, parser):#Add command line argument flush
        # Positional arguments
        parser.add_argument("--flush",action="store_true",help="Empty movies app tables before import")

    def handle(self, *args, **options):
        # If a user chooses to flush, then flush movies app related tables from the database before the import
        if(options["flush"]):
            flush_movies(self)

        # TODO: add user path and more error handling later
        moviesPath = Path(os.getenv('MOVIES_PATH')).expanduser()
        creditsPath = Path(os.getenv('CREDITS_PATH')).expanduser()

        logger.info('Import started')
        self.stdout.write(self.style.NOTICE('Import started'))

        movies = self.get_movies_df(moviesPath, creditsPath)

        # Get unique dicts multi value cell column cells
        genres = self.unique_list_from_list_col(movies["genres"])
        casts = self.unique_list_from_list_col(movies["cast"])
        crews = self.unique_list_from_list_col(movies["crew"])

        genre_objects = self.create_genre_objects(genres)
        casts_objects = self.create_persona_objects(casts)
        crews_objects = self.create_persona_objects(crews)

        genre_objects2 = self.add_genre_elements_to_db(genre_objects)
        casts_objects2, crews_objects2 = self.add_persona_elements_to_db(casts_objects, crews_objects)

        genres = self.dictify(genres, genre_objects2)
        casts = self.dictify(casts, casts_objects2)
        crews = self.dictify(crews, crews_objects2)

        movie_objects = self.create_movie_objects(movies)

        movie_objects = self.add_movies_to_db(movie_objects)

        self.add_relationships(movies, movie_objects, genres, casts, crews)

        logger.info('Import completed')
        self.stdout.write(self.style.SUCCESS('Import completed'))


    def get_movies_df(self, moviePath: str, creditsPath: str) -> pd.DataFrame:
        movies = pd.read_csv(
            moviePath,
            usecols=['id', 'title', 'genres', 'overview', 'tagline', 'release_date', 'runtime'],
            low_memory=False,
            encoding="utf8",
            infer_datetime_format=True)
        #TODO: Use full dataset in final version
        movies = movies.head(1000)#Get first 1000 rows

        # get credits dataframe (more info on cast/directors)
        credits = pd.read_csv(creditsPath, encoding="utf8")

        movies = pd.merge(movies, credits, on="id")
        movies["genres"] = movies["genres"].apply(self.str_dict_to_unique_list)
        movies["cast"] = movies["cast"].apply(self.str_dict_to_unique_list)
        movies["crew"] = movies["crew"].apply(self.str_dict_to_unique_director_list)

        movies=movies[["id", "title", "genres", "tagline", "overview", "cast", "crew", "release_date", "runtime"]]
        movies.dropna(inplace=True)# Drop all rows that have na values that matter to us
        movies.drop_duplicates(subset=["id"],inplace=True)# Only keep movies with the right id
        return movies

    def add_relationships(self, movies, movie_objects: list[Movie], genres: dict[str, Genre], casts: dict[str, Persona], crews: dict[str, Persona]):
        genre_relations = list()
        actor_relations = list()
        director_relations = list()
        i = 0

        for _, row in movies.iterrows():
            movie = movie_objects[i]
            for genre in row["genres"]:
                genre_relations.append(movie.genres.through(genre_id=genres[genre].id, movie_id=movie.id))
            for cast in row["cast"]:
                actor_relations.append(movie.actors.through(persona_id=casts[cast].id, movie_id=movie.id))
            for director in row["crew"]:
                director_relations.append(movie.directors.through(persona_id=crews[director].id, movie_id=movie.id))
            i += 1

        logger.info('Adding movie relationships')
        Movie.genres.through.objects.bulk_create(genre_relations)
        Movie.actors.through.objects.bulk_create(actor_relations)
        Movie.directors.through.objects.bulk_create(director_relations)

    # |---------------------------------------------------------------
    # | Persisting objects to the database
    # |---------------------------------------------------------------

    # GENRES
    def create_genre_objects(self, genres: list[str]) -> list[Genre]:
        genre_objs = list()

        for genre in genres:
            obj = Genre(name=genre, slug=slugify(genre))
            genre_objs.append(obj)

        return genre_objs

    def add_genre_elements_to_db(self, genres: list[Genre]) -> list[Genre]:
        try:
            logger.info('Adding genres')
            return Genre.objects.bulk_create(genres)

        except IntegrityError as e:
            logger.warning("Genre insertion error: " + str(e))
            return list()

    # PERSONA
    def create_persona_objects(self, persona: list[str]) -> list[Persona]:
        persona_objs = list()

        for person in persona:
            obj = Persona(full_name=person)
            persona_objs.append(obj)

        return persona_objs

    def add_persona_elements_to_db(self, casts: list[Persona], crews: list[Persona]) -> list[list[Persona], list[Persona]]:
        try:
            logger.info('Adding cast and crew')
            newCast = Persona.objects.bulk_create(casts)
            newCrew = Persona.objects.bulk_create(crews)
            return newCast,newCrew

        except IntegrityError as e:
            logger.warning("Persona insertion error: " + str(e))
            return [list(), list()]

    # MOVIES
    def create_movie_objects(self, movies: pd.DataFrame) -> list[Movie]:
        #TODO: add ratings and trailer later, maybe split class up so we don't do too much at once
        movie_objects=list()

        for _, row in movies.iterrows():
            movie_slug=slugify(row["title"]+"-"+str(+row["id"]))# Title alone is not always unique
            filename = '{}.jpg'.format(row["id"])
            poster_path = os.path.join(settings.POSTERS_PATH, filename)
            placeholder_path = os.path.join(settings.POSTERS_PATH, 'poster_placeholder.png')

            movie = Movie(
                id=row["id"],
                title=row["title"],
                slug=movie_slug,
                length=row["runtime"],
                released_on=row["release_date"],
                # Not all movies have a poster
                poster_path=poster_path if os.path.exists(poster_path) else placeholder_path,
                plot=row["overview"])
            movie_objects.append(movie)

        return movie_objects

    def add_movies_to_db(self, movies: list[Movie]) -> list[Movie]:
        try:
            logger.info('Adding movies')
            return Movie.objects.bulk_create(movies)
        except IntegrityError as e:
            logger.warning("Movie insertion error: " + str(e))
            return list()

    # |---------------------------------------------------------------
    # | Helper functions
    # |---------------------------------------------------------------

    def str_dict_to_unique_list(self, genres) -> list[str]:
        genre_aslist = eval(genres)
        return list(set(g["name"] for g in genre_aslist))

    def str_dict_to_unique_director_list(self, genres) -> list[str]:
        genre_aslist = eval(genres)
        return list(set(g["name"] for g in genre_aslist if g["department"] == "Directing"))

    def unique_list_from_list_col(self, list_col) -> list[str]:
        return list(set(itertools.chain.from_iterable(list_col)))
    
    # Combine 2 lists with the same length and a fitting order together
    def dictify(self, keys: list, vals: list):
        obj_dict = dict()

        for i in range(len(keys)):
            obj_dict[keys[i]] = vals[i]

        return obj_dict
