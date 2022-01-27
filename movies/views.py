import os
import random

from django.shortcuts import render
import datetime

# Create your views here.
from movies.models import Movie
from django.contrib.staticfiles import finders


def index(request):
    now = datetime.datetime.now()
    feature_movies = get_features_movies()
    recommended_movies = get_recommended_movies()
    return render(request, 'index.html', {'now': now,
                                          'featured_movie_list': feature_movies,
                                          'recommended_movie_list': recommended_movies
                                          })


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
