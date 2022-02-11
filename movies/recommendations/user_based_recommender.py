import copy
import sys
from math import sqrt
from django.db.models import QuerySet, Count, Avg
from django.contrib.auth.models import User
from movies.models import Rating, Movie, Genre


class UserBasedRecommender:
    def __init__(self, user_id: int,movies_in_common_threshhold=5, similar_user_amount=20, popular_movie_date_threshhold="2000-01-01",decent_rating_threshhold=5):
        self.movies_in_common_threshhold = movies_in_common_threshhold
        self.similar_user_amount = similar_user_amount
        self.popular_movie_date_threshhold=popular_movie_date_threshhold
        self.decent_rating_threshhold = decent_rating_threshhold
        #Only calculate this data one time (instead of multiple times) to save computation time
        self.user_id=user_id
        #self.ratings= Rating.objects.filter(user=user_id)
        #self.rated_movie_ids = self.ratings.values_list("movie", flat=True).distinct()

        self.rated_movies = Movie.objects.filter(rating__user=user_id)
        self.ratings = Rating.objects.filter(user=user_id)

        #self.movies = Movie.objects.annotate(rating_count=Count("rating"))
        self.other_movies = Movie.objects.exclude(id__in=self.rated_movies.values_list("id", flat=True))
        self.other_movies = self.other_movies.annotate(rating_count=Count("rating")).annotate(voting_avg=Avg("rating__rating"))
        self.other_ratings = Rating.objects.filter(movie__in=self.other_movies.values_list("id", flat=True))

    def get_popular_recommendations(self,num_recommendations,already_suggested_movie_ids=list()) -> QuerySet[Movie]:#Get popular movies for user

        other_movies = self.other_movies
        if (len(already_suggested_movie_ids) > 0):
            other_movies = self.other_movies.exclude(id__in=already_suggested_movie_ids)

        movies = other_movies.exclude(released_on__lte=self.popular_movie_date_threshhold).values_list("id", flat=True)
        movies = movies.filter(voting_avg__gt=self.decent_rating_threshhold)

        sorted_movies = other_movies.filter(id__in=movies).order_by('-rating_count')[:num_recommendations].values_list("id", flat=True)
        if(len(sorted_movies) < num_recommendations): #In case we have too little matches, take less preferable options
            rating_amount = num_recommendations - len(sorted_movies)
            alternative_movies = other_movies.exclude(id__in=sorted_movies)#.values_list("id", flat=True)
            sorted_movies2 = alternative_movies.order_by('-rating_count')[:rating_amount].values_list("id",flat=True)
            sorted_movies = sorted_movies.union(sorted_movies2) #Combine querysets

        return Movie.objects.filter(id__in=sorted_movies)

    def get_top_recommendations(self, num_recommendations, already_suggested_movie_ids=list()) -> QuerySet[Movie]:#Get the best movies based on similar users
        similarities = self.get_user_similarities()
        return self.get_movies_from_similar_users(similarities, num_recommendations,already_suggested_movie_ids)

    # Get the users favorite genres and recommend popular movies from there
    def get_genre_recommendations(self, num_recommendations, num_genres, already_suggested_movie_ids_original=list()) -> dict[str, QuerySet[Movie]]:

        genres=dict.fromkeys(Genre.objects.values_list("id", flat=True), 0)
        for movie in self.rated_movies:
            for genre in movie.genres.all():
                genres[genre.id] += 1

        top_genres = self.get_top_x_dict(genres, num_genres, True)

        already_suggested_movie_ids = copy.deepcopy(already_suggested_movie_ids_original)
        results = dict()
        for genre_id in top_genres.keys():
            genre_movies = self.other_movies.filter(genres__id=genre_id)
            if (len(already_suggested_movie_ids) > 0):
                genre_movies = genre_movies.exclude(id__in=already_suggested_movie_ids)

            good_genre_movies = genre_movies.filter(voting_avg__gt=self.decent_rating_threshhold)
            sorted_genre_movies = good_genre_movies.order_by('-rating_count')[:num_recommendations].values_list("id", flat=True)

            if (len(sorted_genre_movies) < num_recommendations):  # In case we have too little matches, take less preferable options
                rating_amount = num_recommendations - len(sorted_genre_movies)
                alternative_movies = genre_movies.exclude(id__in=sorted_genre_movies)  # .values_list("id", flat=True)
                sorted_genre_movies2 = alternative_movies.order_by('-rating_count')[:rating_amount].values_list("id", flat=True)
                sorted_genre_movies = sorted_genre_movies.union(sorted_genre_movies2)  # Combine querysets

            genre_name = Genre.objects.get(id=genre_id).name
            results[genre_name] = Movie.objects.filter(id__in=sorted_genre_movies)
            already_suggested_movie_ids.extend(list(results[genre_name].values_list("id", flat=True)))

        return results

    def get_movies_from_similar_users(self, similar_users:dict[int,float],num_recommendations:int, already_suggested_movie_ids:list) -> QuerySet[Movie]:

        # Get all Ratings from other users that the user has not yet rated (And therefore seen) yet
        other_movie_ratings = self.other_ratings.filter(user__in=similar_users.keys())
        if(len(already_suggested_movie_ids)>0):
            other_movie_ratings = other_movie_ratings.exclude(movie__in=already_suggested_movie_ids)

        movie_ids = list(other_movie_ratings.values_list("movie", flat=True).distinct())

        if(len(movie_ids) < num_recommendations): #If we don't have enough movies from our recommended users, add some more popular movies instead
            movie_amount = num_recommendations-len(movie_ids)
            already_suggested = copy.deepcopy(already_suggested_movie_ids)
            already_suggested.extend(movie_ids)

            additional_recommendations = self.get_popular_recommendations(movie_amount, already_suggested)
            for movie in additional_recommendations:
                movie_ids.append(movie.id)


        movie_score = dict.fromkeys(movie_ids, 0)
        for rating in other_movie_ratings:
            movie_score[rating.movie_id] = movie_score[rating.movie_id]+rating.rating*similar_users[rating.user_id]#Add score for every user, based on user rating and the similarity of the user to us

        suggested_movie_dict=self.get_top_x_dict(movie_score,num_recommendations, True)

        return self.other_movies.filter(id__in=suggested_movie_dict.keys())


    def get_user_similarities(self) -> dict[int, int]:

        other_users = User.objects.exclude(id=self.user_id)

        distances = dict()

        for other_user in other_users:
            common_ratings = Rating.objects.filter(user=other_user.id, movie__in=self.rated_movies.values_list("id", flat=True))
            if (common_ratings.count() >= self.movies_in_common_threshhold):#Only add similar user if they have a certain number of movies in common
                distances[other_user.id] = self.euclidian_distance(common_ratings, self.ratings)/common_ratings.count()#Average of total distance

        distances_below_threshhold=dict()
        cur_len = len(distances)
        if(cur_len<self.similar_user_amount):#If our threshhold is too high, also add users below our common ratings threshhold
            for other_user in other_users.exclude(id__in=distances.keys()):
                common_ratings = Rating.objects.filter(user=other_user.id, movie__in=self.rated_movies.values_list("id", flat=True))
                if(common_ratings.count()==0):
                    distances_below_threshhold[other_user.id] = sys.float_info.max
                else:
                    distances_below_threshhold[other_user.id] = self.euclidian_distance(common_ratings, self.ratings) / common_ratings.count()  # Average of total distance

            add_amount = self.similar_user_amount - cur_len

            for user_id, distance in self.get_top_x_dict(distances_below_threshhold, add_amount).items():
                distances[user_id] = distance

        return self.get_top_x_dict(distances,self.similar_user_amount)

    def euclidian_distance(self, common_ratings: QuerySet[Rating],
                           user_ratings: QuerySet[Rating]) -> float:  # sqrt(sum((user rating - other user rating)^2))
        distances = list()
        for other_rating in common_ratings:
            user_rating = user_ratings.get(movie=other_rating.movie)#Get current user rating
            distances.append(pow(user_rating.rating - other_rating.rating, 2))
        return sqrt(sum(distances))


    def get_top_x_dict(self,start_dict,count:int,reverse_order=False): #Return best x users
        return dict(sorted(start_dict.items(), key=lambda item: item[1], reverse=reverse_order)[:count])