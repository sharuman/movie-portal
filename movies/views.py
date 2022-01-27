
import os
import random

from django.shortcuts import render,redirect

import datetime
from django.views import View
# importing needed, created forms from forms.py
from .forms import SignUpForm


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

