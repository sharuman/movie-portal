import os
import random
import string
import names
import pandas as pd
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import Model
from slugify import slugify

from config import settings
from movies.models import Movie, Genre, Persona, Rating


class ObjectCreator:

    # USER
    def create_user_objects(self, users: list[str]) -> dict[int, User]:
        users_objs = dict()

        for user_id in users:
            random_pw = self.rand_str(n=10)
            first_name=names.get_first_name()
            last_name=names.get_last_name()
            random_username = first_name + "_"+ last_name + "_" + str(user_id)
            email=first_name + "."+ last_name + "_" + str(user_id) + "@gmail.com"
            obj = User(id=user_id, username=random_username, password=make_password(random_pw),first_name=first_name, last_name=last_name,email=email)
            users_objs[int(user_id)] = obj

        return users_objs

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
                # Not all movies have a poster
                poster_path=poster_path if os.path.exists(poster_path) else placeholder_path,
                plot=row["overview"])
            movie_objects[row["id"]] = movie

        return movie_objects

    # PERSONA
    def create_persona_objects(self, persona: dict[int, str]) -> dict[int, Persona]:
        persona_objs = dict()

        for id, name in persona.items():
            obj = Persona(id=id, full_name=name)
            persona_objs[id] = obj

        return persona_objs

    # RATING
    def create_rating_objects(self, ratings: pd.DataFrame, movies: dict[int, Movie], users: dict[int, User]) -> list[
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

    # GENRES
    def create_genre_objects(self, genres: dict[int, str]) -> dict[int, Genre]:
        genre_objs = dict()

        for id, name in genres.items():
            obj = Genre(id=id, name=name, slug=slugify(name))
            genre_objs[id] = obj

        return genre_objs

    def create_genre_actor_director_through_objects(self, movies: pd.DataFrame, movie_objects: dict[int, Movie]) -> [list, list, list]:
        genre_relations = list()
        actor_relations = list()
        director_relations = list()

        for _, row in movies.iterrows():
            movie = movie_objects[row["id"]]
            for id in row["genres"].keys():
                genre_relations.append(movie.genres.through(genre_id=id, movie_id=movie.id))
            for id in row["cast"].keys():
                actor_relations.append(movie.actors.through(persona_id=id, movie_id=movie.id))
            for id in row["crew"].keys():
                director_relations.append(movie.directors.through(persona_id=id, movie_id=movie.id))

        return genre_relations, actor_relations, director_relations

    def create_model_objects(self, model_object: Model, id_to_str_dict: dict[int, str]) -> dict[int, Model]:
        if (model_object == Genre):
            return self.create_genre_objects(id_to_str_dict)
        elif (model_object == Persona):
            return self.create_persona_objects(id_to_str_dict)

    def rand_str(self, chars=string.ascii_uppercase + string.digits, n=10):  # Create random string
        return ''.join(random.choice(chars) for _ in range(n))
