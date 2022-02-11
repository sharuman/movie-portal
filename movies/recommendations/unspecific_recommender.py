from django.db.models import Count, Avg

from movies.models import Movie, Genre, Rating


class UnspecificRecommender:
    def __init__(self, popular_movie_date_threshhold="2000-01-01",decent_rating_threshhold=5):
        self.decent_rating_threshhold=decent_rating_threshhold
        self.popular_movie_date_threshhold = popular_movie_date_threshhold
        self.aggregated_movies = Movie.objects.annotate(rating_count=Count("rating")).annotate(voting_avg=Avg("rating__rating"))

    def get_popular_recommendations(self,num_recommendations,already_suggested_movie_ids=list()):#Get popular movies for user

        movies = self.aggregated_movies
        if (len(already_suggested_movie_ids) > 0):
            movies = movies.exclude(id__in=already_suggested_movie_ids)

        other_movies = movies.exclude(released_on__lte=self.popular_movie_date_threshhold)
        other_movies = other_movies.filter(voting_avg__gt=self.decent_rating_threshhold)
        sorted_movies = other_movies.order_by('-rating_count')[:num_recommendations].values_list("id", flat=True)

        if (len(sorted_movies) < num_recommendations):  # In case we have too little matches, take less preferable options
            rating_amount = num_recommendations - len(sorted_movies)
            alternative_movies = movies.exclude(id__in=sorted_movies)  # .values_list("id", flat=True)
            sorted_movies2 = alternative_movies.order_by('-rating_count')[:rating_amount].values_list("id",flat=True)
            sorted_movies = sorted_movies.union(sorted_movies2)  # Combine querysets

        return Movie.objects.filter(id__in=sorted_movies)

    def get_genre_recommendations(self, genre_id, num_recommendations, already_suggested_movie_ids=list()):

        movies = self.aggregated_movies.filter(genres__id=genre_id)
        if (len(already_suggested_movie_ids) > 0):
            movies = movies.exclude(id__in=already_suggested_movie_ids)

        other_movies = movies.filter(voting_avg__gt=self.decent_rating_threshhold)

        sorted_movies = other_movies.order_by('-rating_count')[:num_recommendations].values_list("id", flat=True)

        if (len(sorted_movies) < num_recommendations):  # In case we have too little matches, take less preferable options
            rating_amount = num_recommendations - len(sorted_movies)
            alternative_movies = movies.exclude(id__in=sorted_movies)  # .values_list("id", flat=True)
            sorted_movies2 = alternative_movies.order_by('-rating_count')[:rating_amount].values_list("id", flat=True)
            sorted_movies = sorted_movies.union(sorted_movies2)  # Combine querysets

        return Movie.objects.filter(id__in=sorted_movies)



