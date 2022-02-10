from django.db.models import Count

from movies.models import Movie, Genre, Rating


class UnspecificRecommender:
    def __init__(self, popular_movie_date_threshhold="2010-01-01"):
        self.popular_movie_date_threshhold = popular_movie_date_threshhold
        self.aggregated_ratings = Rating.objects.filter(rating__gt=4).annotate(rating_count=Count("movie"))

    def get_popular_recommendations(self,num_recommendations,already_suggested_movie_ids=list()):#Get popular movies for user

        movies = Movie.objects.all()
        if (len(already_suggested_movie_ids) > 0):
            movies=movies.exclude(id__in=already_suggested_movie_ids)

        movies = movies.exclude(released_on__lte=self.popular_movie_date_threshhold)

        sorted_ratings = self.aggregated_ratings.filter(movie__in=movies).order_by('rating_count')[
                         :num_recommendations]  # Get ratings and sort them based on rating count/movie

        return Movie.objects.filter(id__in=sorted_ratings.values_list("movie", flat=True))

    def get_genre_recommendations(self, genre_id, num_recommendations, already_suggested_movie_ids=list()):

        movies = Movie.objects.filter(genres__id=genre_id)
        if (len(already_suggested_movie_ids) > 0):
            movies = movies.exclude(id__in=already_suggested_movie_ids)

        sorted_ratings = self.aggregated_ratings.filter(movie__in=movies).order_by('rating_count')[
                         :num_recommendations]  # Get ratings and sort them based on rating count/movie

        results = Movie.objects.filter(id__in=sorted_ratings.values_list("movie", flat=True))
        return results



