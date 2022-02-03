import random
import string

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Model
from django.db.utils import IntegrityError
from pathlib import Path
import pandas as pd
import os
import logging
from slugify import slugify
from django.conf import settings

from movies.management.commands.flush_movies import flush_movies
from movies.models import Genre, Movie, Persona, Rating
import numpy as np

# TODO: Discuss, how and when logger should be used
logger = logging.getLogger('command_import_movies')


class Command(BaseCommand):
    help = 'Import movies and the main relationships'

    def add_arguments(self, parser):  # Add command line argument flush
        # Positional arguments
        parser.add_argument("--flush", action="store_true", help="Empty movies app tables before import")

    def handle(self, *args, **options):
        # If a user chooses to flush, then flush movies app related tables from the database before the import
        if (options["flush"]):
            flush_movies(self)

        # TODO: add user path and more error handling later
        movies_path = Path(os.getenv('MOVIES_PATH')).expanduser()
        credits_path = Path(os.getenv('CREDITS_PATH')).expanduser()
        ratings_path = Path(os.getenv('RATINGS_PATH')).expanduser()

        logger.info('Import started')
        self.stdout.write(self.style.NOTICE('Import started'))

        movies_df = self.get_movies_df(movies_path, credits_path)
        ratings_df = self.get_ratings_df(ratings_path)

        # Insert tables with similar logic via generic function (Genre/Persona)
        self.dict_col_insert(movies_df["genres"], "Genre", Genre)
        self.dict_col_insert(movies_df["cast"], "Cast", Persona)
        self.dict_col_insert(movies_df["crew"], "Crew", Persona)

        # Add Users
        users = ratings_df["userId"].unique()
        user_objects = self.create_user_objects(users)  # Since those are user ratings, we need the users and ratings
        users = self.model_list_to_model_dict(list(user_objects.values()))
        self.add_elements_to_db(list(user_objects.values()), "User", User)

        # Add movies
        movie_objects = self.create_movie_objects(movies_df)
        movies = self.model_list_to_model_dict(list(movie_objects.values()))
        self.add_elements_to_db(list(movie_objects.values()), "Movie", Movie)

        # Add movie relations
        self.add_relationships(movies_df, movies)

        # Add ratings
        rating_objects = self.create_rating_objects(ratings_df, movies, users)
        self.add_elements_to_db(rating_objects, "Rating", Rating)

        logger.info('Import completed')
        self.stdout.write(self.style.SUCCESS('Import completed'))

    def dict_col_insert(self, dict_col: pd.DataFrame, model_name: str, model_object: Model):
        id_to_str_dict = self.dict_from_dict_col(dict_col)
        id_to_model_dict = self.create_model_objects(model_object,id_to_str_dict)
        self.add_elements_to_db(list(id_to_model_dict.values()), model_name, model_object)

    def create_model_objects(self, model_object:Model, id_to_str_dict:dict[int,str])-> dict[int,Model]:
        if (model_object == Genre):
            return self.create_genre_objects(id_to_str_dict)
        elif (model_object == Persona):
            return self.create_persona_objects(id_to_str_dict)

    def convert_to_int_or_nan(self, val: str):  # Either return an int, or if this is not possible, a nan value
        try:
            return int(val)
        except ValueError:
            return np.nan

    def get_ratings_df(self, ratings_path) -> pd.DataFrame:
        ratings = pd.read_csv(
            ratings_path,
            usecols=['userId', 'movieId', 'rating'],
            dtype={"userId": np.int64, "movieId": np.int64},
            low_memory=False,
            encoding="utf8",
            infer_datetime_format=True)
        ratings = ratings.head(1000)  # Get first 1000 rows
        return ratings

    def get_movies_df(self, movies_path: str, credits_path: str) -> pd.DataFrame:
        movies = pd.read_csv(
            movies_path,
            usecols=['id', 'title', 'genres', 'overview', 'tagline', 'release_date', 'runtime'],
            low_memory=False,
            encoding="utf8",
            infer_datetime_format=True)

        movies["id"].apply(
            self.convert_to_int_or_nan)  # The ids of the dataset are not clean (non numbers inside), so we actually have to get them into a proper format
        movies.dropna(inplace=True)  # Drop all rows that have na values that matter to us -> Also invalid id rows
        movies = movies.astype({'id': np.int64},
                               copy=False)  # Now we can set the column to the proper type without getting an error because the conversion doesn't work

        # TODO: Use full dataset in final version
        movies = movies.head(1000)  # Get first 1000 rows

        # get credits dataframe (more info on cast/directors)
        credits_df = pd.read_csv(credits_path,
                                 encoding="utf8")  # We don't call it credits, because it is already a built in function
        credits_df.dropna(inplace=True)  # Drop all rows that have na values that matter to us

        movies = pd.merge(movies, credits_df, on="id")  # Match the two dataframes on id

        # Convert from a string representation of a dict to an actual list
        movies["genres"] = movies["genres"].apply(self.str_dict_to_dict)
        movies["cast"] = movies["cast"].apply(self.str_dict_to_dict)
        movies["crew"] = movies["crew"].apply(self.str_dict_to_director_dict)

        movies = movies[["id", "title", "genres", "tagline", "overview", "cast", "crew", "release_date", "runtime"]]
        movies.drop_duplicates(subset=["id"], inplace=True)  # Only keep merged rows where everything is there
        return movies

    def add_relationships(self, movies, movie_objects: dict[int, Movie]):
        genre_relations = list()
        actor_relations = list()
        director_relations = list()
        i = 0

        for _, row in movies.iterrows():
            movie = movie_objects[row["id"]]
            for id in row["genres"].keys():
                genre_relations.append(movie.genres.through(genre_id=id, movie_id=movie.id))
            for id in row["cast"].keys():
                actor_relations.append(movie.actors.through(persona_id=id, movie_id=movie.id))
            for id in row["crew"].keys():
                director_relations.append(movie.directors.through(persona_id=id, movie_id=movie.id))
            i += 1

        logger.info('Adding movie relationships')
        Movie.genres.through.objects.bulk_create(genre_relations)
        Movie.actors.through.objects.bulk_create(actor_relations)
        Movie.directors.through.objects.bulk_create(director_relations)

    # |---------------------------------------------------------------
    # | Persisting objects to the database
    # |---------------------------------------------------------------

    # GENRES
    def create_genre_objects(self, genres: dict[int, str]) -> dict[int, Genre]:
        genre_objs = dict()

        i = 0
        for id, name in genres.items():
            obj = Genre(id=id, name=name, slug=slugify(name))
            genre_objs[id] = obj
            i += 1

        return genre_objs

    # PERSONA
    def create_persona_objects(self, persona: dict[int, str]) -> dict[int, Persona]:
        persona_objs = dict()

        for id, name in persona.items():
            obj = Persona(id=id, full_name=name)
            persona_objs[id] = obj

        return persona_objs

    # GENERIC
    def add_elements_to_db(self, elements: list[Model], model_name: str, model_object: Model) -> list[Model]:
        try:
            logger.info('Adding ' + model_name)
            return model_object.objects.bulk_create(elements, ignore_conflicts=True)

        except IntegrityError as e:
            logger.warning(model_name + " insertion error: " + str(e))
            return list()

    def create_user_objects(self, users: list[str]) -> dict[int, User]:
        users_objs = dict()

        for user_id in users:
            random_pw = self.rand_str(n=10)
            random_username = self.rand_str(n=10) + "_" + str(user_id)
            obj = User(id=user_id, username=random_username, password=random_pw)
            users_objs[user_id] = obj

        return users_objs

    def create_rating_objects(self, ratings: pd.DataFrame, movies: dict[id, Movie], users: dict[id, User]) -> list[
        Rating]:
        ratings_objs = list()

        for row_id, row in ratings.iterrows():
            movie_id = row["movieId"]
            user_id = row["userId"]

            try:  # TODO: Add handling later
                obj = Rating(movie=movies[movie_id], user=users[user_id], rating=row["rating"])
                ratings_objs.append(obj)
            except:
                pass

        return ratings_objs

    # MOVIES
    def create_movie_objects(self, movies: pd.DataFrame) -> dict[id, Movie]:
        # TODO: add ratings and trailer later, maybe split class up so we don't do too much at once
        movie_objects = dict()

        for _, row in movies.iterrows():
            movie_slug = slugify(row["title"] + "-" + str(+row["id"]))  # Title alone is not always unique
            filename = '{}.jpg'.format(row["id"])
            poster_path = os.path.join(settings.POSTERS_PATH, filename)
            placeholder_path = os.path.join(settings.POSTERS_PATH, 'poster_placeholder.png')

            movie = Movie(
                id=row["id"],
                title=row["title"],
                slug=movie_slug,
                length=row["runtime"],
                released_on=row["release_date"],
                trailer="",
                # Not all movies have a poster
                poster_path=poster_path if os.path.exists(poster_path) else placeholder_path,
                plot=row["overview"])
            movie_objects[row["id"]] = movie

        return movie_objects

    # |---------------------------------------------------------------
    # | Helper functions
    # |---------------------------------------------------------------

    def str_dict_to_dict(self, str_dict) -> dict[int, str]:
        genre_aslist = eval(str_dict)
        all_entries = dict()

        for g in genre_aslist:
            all_entries[g["id"]] = g["name"]

        return all_entries

    def str_dict_to_director_dict(self, str_dict) -> dict[int, str]:
        genre_aslist = eval(str_dict)
        all_entries = dict()
        for g in genre_aslist:
            if g["department"] == "Directing":
                all_entries[g["id"]] = g["name"]

        return all_entries

    def dict_from_dict_col(self, dict_col) -> dict[int, str]:
        unique_dict = dict()
        for row_dict in dict_col.values:
            for id, name in row_dict.items():
                unique_dict[id] = name

        return unique_dict

    def rand_str(self, chars=string.ascii_uppercase + string.digits, n=10):  # Create random string
        return ''.join(random.choice(chars) for _ in range(n))

    def get_all_fields(self, model: Model) -> list[str]:
        all_fields = list()
        for field in model._meta.get_fields(include_parents=False):
            if (field.concrete and not field.many_to_many and not field.primary_key):
                all_fields.append(field.name)
        return all_fields

    # Combine 2 lists with the same length and a fitting order together
    def model_list_to_model_dict(self, models: list[Model]) -> dict[int, Model]:
        obj_dict = dict()

        for model in models:
            obj_dict[model.id] = model

        return obj_dict

    # Combine 2 lists with the same length and a fitting order together
    def dictify(self, keys: list, vals: list):
        obj_dict = dict()

        for i in range(len(keys)):
            obj_dict[keys[i]] = vals[i]

        return obj_dict
