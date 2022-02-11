import pandas as pd
import pytest
from django.contrib.auth.models import User

from movies.management.commands.import_utils.object_creation import ObjectCreator


# Helper functions

#pytestmark = pytest.mark.django_db#
from movies.models import Movie, Persona, Rating


@pytest.mark.django_db(transaction=True)
def create_random_user() -> [int, User]:
    user_id = 1
    object_creator = ObjectCreator()
    users = object_creator.create_user_objects(list([user_id]))
    user = users[user_id]
    return user_id, user

@pytest.mark.django_db(transaction=True)
def create_random_movie() -> [int, Movie]:
    movie_id = 1
    movie_df = pd.DataFrame({"id": [movie_id], "title": ["mytitle"], "runtime": [100], "release_date": ["2000-01-01"], "overview": ["myoverview"]})
    object_creator = ObjectCreator()
    movies = object_creator.create_movie_objects(movie_df)
    movie = movies[movie_id]
    return movie_id, movie

@pytest.mark.django_db(transaction=True)
def create_random_persona() -> [int, Persona]:
    persona_id = 1
    object_creator = ObjectCreator()
    personas = object_creator.create_persona_objects({persona_id: "MyPersona"})
    persona = personas[persona_id]
    return persona_id, persona


@pytest.mark.django_db(transaction=True)
def create_random_rating() -> [int, int, Persona]:
    movie_id, movie = create_random_movie()
    movie.save()

    user_id, user = create_random_user()
    user.save()

    object_creator = ObjectCreator()
    ratings_df = pd.DataFrame({"movieId": [movie_id], "userId": [user_id], "rating": [1]})
    ratings = object_creator.create_rating_objects(ratings_df, {movie_id: movie}, {user_id: user})
    rating = ratings[0]
    return movie_id, user_id, rating
# Tests


@pytest.mark.django_db(transaction=True)
def test_create_user_object():
    user_id, user = create_random_user()

    assert user.id == user_id
    assert not user.is_staff


@pytest.mark.django_db(transaction=True)
def test_add_user_object():
    user_id, user = create_random_user()
    user.save()
    user_from_db = User.objects.get(id=user_id)
    assert user == user_from_db

@pytest.mark.django_db(transaction=True)
def test_create_movie_object():
    movie_id, movie = create_random_movie()
    assert movie.id == movie_id


@pytest.mark.django_db(transaction=True)
def test_add_movie_object():
    movie_id, movie = create_random_movie()
    movie.save()
    user_from_db = Movie.objects.get(id=movie_id)
    assert movie == user_from_db

@pytest.mark.django_db(transaction=True)
def test_create_persona_object():
    persona_id, persona = create_random_persona()
    assert persona.id == persona_id


@pytest.mark.django_db(transaction=True)
def test_add_persona_object():
    persona_id, persona = create_random_persona()
    persona.save()
    persona_from_db = Persona.objects.get(id=persona_id)
    assert persona == persona_from_db


@pytest.mark.django_db(transaction=True)
def test_create_rating_object():
    movie_id, user_id, rating = create_random_rating()
    assert rating.movie_id == movie_id
    assert rating.user_id == user_id


@pytest.mark.django_db(transaction=True)
def test_add_rating_object():
    movie_id, user_id, rating = create_random_rating()
    rating.save()
    rating_from_db = Rating.objects.get(movie=movie_id, user=user_id)
    assert rating == rating_from_db
