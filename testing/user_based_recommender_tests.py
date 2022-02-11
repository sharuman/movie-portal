import pandas as pd
import pytest
from django.db.models import Avg

from movies.management.commands.import_utils.object_creation import ObjectCreator
from movies.models import Movie
from movies.recommendations.user_based_recommender import UserBasedRecommender


@pytest.mark.django_db(transaction=True)
def add_mock_data_to_db():
    object_creator = ObjectCreator()

    users = object_creator.create_user_objects(list([1, 2, 3]))
    for user in users.values():
        user.save()

    genres = object_creator.create_genre_objects({1: "Adventure", 2: "Fantasy", 3: "Action"})
    for genre in genres.values():
        genre.save()

    movie_df = pd.DataFrame({"id": [1, 2, 3], "title": ["Avatar", "James Bond", "Indiana Jones"], "runtime": [110, 100, 90], "release_date": ["2016-01-01","2018-01-01","2000-01-01"],
                             "overview": ["aliens", "agent", "adventurer"]})
    movies = object_creator.create_movie_objects(movie_df)
    for movie in movies.values():
        movie.save()

    movies[1].genres.add(genres[2])
    movies[1].genres.add(genres[3])
    movies[1].save()

    movies[2].genres.add(genres[3])
    movies[2].genres.add(genres[1])
    movies[2].save()

    movies[3].genres.add(genres[1])
    #movies[3].genres.add(genres[3])
    movies[3].save()

    ratings_df = pd.DataFrame({"movieId": [3, 3, 3, 1, 1, 2], "userId": [1, 2, 3, 2, 3, 2], "rating": [6, 5, 6, 8, 7, 6]})
    #If we take 1:
        #Movie Number 3 is the most rated one
        #User Number 3 is closest to our user
        #User likes the genres of indiana jones the most (in our case: Fantasy, Adventure)
        #User must not be suggested movie number 3

    ratings = object_creator.create_rating_objects(ratings_df, movies, users)
    for rating in ratings:
        rating.save()


@pytest.mark.django_db(transaction=True)
def test_popular_movies():
    movie_count=1
    add_mock_data_to_db()
    user_based_recommender = UserBasedRecommender(1)
    recommendations = user_based_recommender.get_popular_recommendations(movie_count)
    assert len(recommendations) == movie_count #Right amount of output movies
    assert recommendations[0].id == 1 #Most popular movie in dataset is avatar, it should be avatar


@pytest.mark.django_db(transaction=True)
def test_recommended_movies():
    movie_count = 1
    add_mock_data_to_db()
    user_based_recommender = UserBasedRecommender(1,movies_in_common_threshhold=1)
    recommendations = user_based_recommender.get_top_recommendations(movie_count)
    assert len(recommendations) == movie_count
    assert recommendations[0].id == 1 #Most popular movie in dataset is avatar, it should be avatar

@pytest.mark.django_db(transaction=True)
def test_genre_movies():
    movie_count = 1
    add_mock_data_to_db()
    user_based_recommender = UserBasedRecommender(1,movies_in_common_threshhold=1)
    recommendations = user_based_recommender.get_genre_recommendations(movie_count, 1)
    assert len(recommendations) == movie_count
    assert recommendations["Adventure"][:1].get().id == 2 #Most popular movie in dataset is avatar, it should be avatar