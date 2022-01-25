from django.shortcuts import render
import datetime

# Create your views here.
from movies.models import Movie


def index(request):
    now = datetime.datetime.now()
    feature_movies=get_features_movies()
    return render(request, 'index.html', {'now': now,'featured_movie_list':feature_movies})











def get_features_movies()->list[Movie]:
    return Movie.objects.all()[:5]
