import os
import random
from django.shortcuts import render, redirect
import datetime
from django.shortcuts import render,redirect
from django.views import View
from .forms import SignUpForm
from movies.models import Movie, Genre
from django.contrib.postgres.search import SearchVector
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UserProfileForm
from .recommendation import getTfIdfRecommendations
from .recommendations.unspecific_recommender import UnspecificRecommender

from .recommendations.user_based_recommender import UserBasedRecommender


recommendation_cache = dict() #For faster and better presentation, precalculate results


def index(request):


    movie_lists=dict()

    num_recommendations = 20

    if(request.user.is_authenticated):
        user_id = request.user.id

        if(user_id in recommendation_cache):
            movie_lists = recommendation_cache[user_id]
        else:
            user_based_recommender = UserBasedRecommender(user_id)

            feature_movies = user_based_recommender.get_popular_recommendations(num_recommendations)  # Get popular movies
            movie_lists["Popular Movies"] = feature_movies
            feature_movie_ids = list(feature_movies.values_list("id", flat=True))

            recommended_movies = user_based_recommender.get_top_recommendations(num_recommendations,
                                                                                feature_movie_ids)  # Get recommended movies that are not already in featured movies
            movie_lists["Users like you like these movies"] = recommended_movies
            recommended_movie_ids = list(recommended_movies.values_list("id", flat=True))
            feature_movie_ids.extend(recommended_movie_ids)

            genre_movies = user_based_recommender.get_genre_recommendations(num_recommendations, 2,
                                                                            feature_movie_ids)  # Get recommendations based on the users favorite genre

            for genre, movies_list in genre_movies.items():
                movie_lists["Because you like " + genre] = movies_list

            recommendation_cache[user_id] = movie_lists

    else:
        unspecific_recommender = UnspecificRecommender()
        feature_movies = unspecific_recommender.get_popular_recommendations(num_recommendations)  # Get popular movies
        movie_lists["Popular Movies"] = feature_movies
        feature_movie_ids = list(feature_movies.values_list("id", flat=True))

        for genre in Genre.objects.all()[:3]:
            genre_movies = unspecific_recommender.get_genre_recommendations(genre.id, num_recommendations, feature_movie_ids)  # Get recommendations based on the users favorite genre
            movie_lists[genre.name] = genre_movies
            feature_movie_ids.extend(list(genre_movies.values_list("id", flat=True)))

    return render(request, 'index.html', {
        'movie_lists': movie_lists
    })

def search(request):
    needle = request.GET.get("q")
    print('Needle:', needle)
    results = Movie.objects.annotate(search=SearchVector('title', 'plot', config='english')).filter(search=needle)
    print(results)
    if(not results):
        print('No results found')
        return render(request, 'search_results.html', {'error': 'No results found'})
    else:
        return render(request, 'search_results.html', {'movies': results, 'needle': needle})

def movie_details(request, slug: str):
    try:
        movie = Movie.objects.get(slug=slug)
        recommendations = getTfIdfRecommendations(movie.id)
        print(recommendations)
        return render(request, 'movie_details.html', {'movie': movie, 'recommendations': recommendations})
    except Exception as e:
        return render(request, 'movie_details.html', {'error': e})

class SignUpView(View):
    form_class = SignUpForm
    initial = {'key': 'value'}
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()        
            return redirect(to='/')
        else:
            return render(request, self.template_name, {'form': form})

@login_required
def user_profile(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)

        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect(to='profile')
    else:
        profile_form = UserProfileForm(instance=request.user.userprofile)

    return render(request, 'user_profile.html', {'profile_form': profile_form, 'error': 'Profile does not exist.'})
