import os
import random
from django.shortcuts import render,redirect
import datetime
from django.views import View
from .forms import SignUpForm
from movies.models import Movie
from django.contrib.staticfiles import finders
from django.contrib.postgres.search import SearchVector

from .recommendations.user_based_recommender import UserBasedRecommender


def index(request):
    feature_movies = list()
    recommended_movies = list()
    genre_movies = dict()


    if(request.user.is_authenticated):
        user_id = request.user.id

        user_based_recommender = UserBasedRecommender(user_id)

        feature_movies = user_based_recommender.get_popular_recommendations(20)  # Get popular movies
        feature_movie_ids = list(feature_movies.values_list("id", flat=True))

        recommended_movies = user_based_recommender.get_top_recommendations(20,
                                                                            feature_movie_ids)  # Get recommended movies that are not already in featured movies
        recommended_movie_ids = list(recommended_movies.values_list("id", flat=True))
        feature_movie_ids.extend(recommended_movie_ids)

        genre_movies = user_based_recommender.get_genre_recommendations(10, 2,
                                                                        feature_movie_ids)  # Get recommendations based on the users favorite genre
    else:
        genre_movies["genre1"] = list()
        genre_movies["genre2"] = list()

    keys = list(genre_movies.keys())

    return render(request, 'index.html', {
        'featured_movie_list': feature_movies,
        'recommended_movie_list': recommended_movies,
        'genre1_name': keys[0],
        'genre1_movie_list': genre_movies[keys[0]],
        'genre2_name': keys[1],
        'genre2_movie_list': genre_movies[keys[1]]
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

def get_50_movies_with_pictures():  # temporary helper function
    all_movies = Movie.objects.all()
    samples = random.sample(list(all_movies), 200)
    valid_samples = list()

    basePath = finders.find("images/posters")

    for sample in samples:
        fullPath = os.path.join(basePath, str(sample.id) + ".jpg")
        if (os.path.exists(fullPath)):
            valid_samples.append(sample)
            if (len(valid_samples) >= 50):
                return valid_samples


def get_features_movies() -> list[Movie]:
    return get_50_movies_with_pictures()


def get_recommended_movies() -> list[Movie]:
    return get_50_movies_with_pictures()


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
