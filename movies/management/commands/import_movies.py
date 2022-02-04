

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Model
from django.db.utils import IntegrityError
import pandas as pd
import logging
from movies.management.commands.import_utils.data_reader import DataFrameReader
from movies.management.commands.import_utils.object_creation import ObjectCreator
from movies.management.commands.flush_movies import flush_movies
from movies.models import Genre, Movie, Persona, Rating

# TODO: Discuss, how and when logger should be used
logger = logging.getLogger('command_import_movies')


class Command(BaseCommand):
    help = 'Import movies and the main relationships'

    def add_arguments(self, parser):  # Add command line argument flush
        # Positional arguments
        parser.add_argument("--flush", action="store_true", help="Empty movies app tables before import")
        parser.add_argument("-max_rows", default=1000, type=int)
    def handle(self, *args, **options):
        # If a user chooses to flush, then flush movies app related tables from the database before the import
        if (options["flush"]):
            flush_movies(self)

        max_rows = options["max_rows"]
        df_reader = DataFrameReader()

        logger.info('Import started')
        self.stdout.write(self.style.NOTICE('Import started'))

        movies_df = df_reader.get_movies_df(max_rows)
        ratings_df = df_reader.get_ratings_df(max_rows)

        creator = ObjectCreator()

        # Insert tables with similar logic via generic function (Genre/Persona)
        self.dict_col_insert(movies_df["genres"], "Genre", Genre, creator)
        self.dict_col_insert(movies_df["cast"], "Cast", Persona, creator)
        self.dict_col_insert(movies_df["crew"], "Crew", Persona, creator)

        # Add Users
        users = ratings_df["userId"].unique()
        user_objects = creator.create_user_objects(users)  # Since those are user ratings, we need the users and ratings
        users = self.model_list_to_model_dict(list(user_objects.values()))
        self.add_elements_to_db(list(user_objects.values()), "User", User)

        # Add movies
        movie_objects = creator.create_movie_objects(movies_df)
        movies = self.model_list_to_model_dict(list(movie_objects.values()))
        self.add_elements_to_db(list(movie_objects.values()), "Movie", Movie)

        genre_throughs, actor_throughs, director_throughs = creator.create_genre_actor_director_through_objects(movies_df,
                                                                                                                movies)
        # Add movie relations
        self.add_throughs_to_database(genre_throughs, actor_throughs, director_throughs)

        # Add ratings
        rating_objects = creator.create_rating_objects(ratings_df, movies, users)
        self.add_elements_to_db(rating_objects, "Rating", Rating)

        logger.info('Import completed')
        self.stdout.write(self.style.SUCCESS('Import completed'))

    def dict_col_insert(self, dict_col: pd.DataFrame, model_name: str, model_object: Model, creator: ObjectCreator):
        id_to_str_dict = self.dict_from_dict_col(dict_col)
        id_to_model_dict = creator.create_model_objects(model_object, id_to_str_dict)
        self.add_elements_to_db(list(id_to_model_dict.values()), model_name, model_object)

    # |---------------------------------------------------------------
    # | Persisting objects to the database
    # |---------------------------------------------------------------

    # GENERIC
    def add_elements_to_db(self, elements: list[Model], model_name: str, model_object: Model) -> list[Model]:
        try:
            logger.info('Adding ' + model_name)
            return model_object.objects.bulk_create(elements, ignore_conflicts=True)

        except IntegrityError as e:
            logger.warning(model_name + " insertion error: " + str(e))
            return list()

    def add_throughs_to_database(self, genre_throughs: list, actor_throughs: list, director_throughs: list):

        logger.info('Adding movie relationships')
        Movie.genres.through.objects.bulk_create(genre_throughs, ignore_conflicts=True)
        Movie.actors.through.objects.bulk_create(actor_throughs, ignore_conflicts=True)
        Movie.directors.through.objects.bulk_create(director_throughs, ignore_conflicts=True)
    # |---------------------------------------------------------------
    # | Helper functions
    # |---------------------------------------------------------------

    def dict_from_dict_col(self, dict_col) -> dict[int, str]:
        unique_dict = dict()
        for row_dict in dict_col.values:
            for id, name in row_dict.items():
                unique_dict[id] = name

        return unique_dict


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
