import os
import random
from django.shortcuts import render,redirect
import datetime
from django.views import View
from .forms import SignUpForm
from movies.models import Movie
from django.contrib.staticfiles import finders
from django.contrib.postgres.search import SearchVector


def index(request):
    now = datetime.datetime.now()
    feature_movies = get_features_movies()
    recommended_movies = get_recommended_movies()
    return render(request, 'index.html', {'now': now,
                                          'featured_movie_list': feature_movies,
                                          'recommended_movie_list': recommended_movies
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
