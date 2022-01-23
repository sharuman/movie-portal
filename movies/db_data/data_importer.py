import itertools

from movies.models import Genre, Movie, Persona
import pandas as pd

def str_dict_to_list(genres):
    genre_aslist = eval(genres)
    return [g["name"] for g in genre_aslist]

def str_dict_to_director_list(genres):
    genre_aslist = eval(genres)
    return [g["name"] for g in genre_aslist if g["department"] == "Directing"]

def unique_dict_from_list_col(list_col):
    return dict.fromkeys(itertools.chain.from_iterable(list_col),None)
    # unique_dict=dict()
    # i=0
    # for val in unique_values:
    #     unique_dict[val]=i
    #     i+=1

    return unique_dict

def fill_movies():
    #Get movies dataframe
    movies = pd.read_csv("movies_metadata.csv.xz", encoding="utf8", infer_datetime_format=True)
    movies["genres"] = movies["genres"].apply(str_dict_to_list)

    #get credits dataframe (more info on cast/directors)
    credits = pd.read_csv("credits.csv.xz", encoding="utf8")

    #merge information
    movies = pd.merge(movies, credits, on="id")

    movies["cast"] = movies["cast"].apply(str_dict_to_list)
    movies["crew"] = movies["crew"].apply(str_dict_to_director_list)
    movies = movies[["id", "title", "genres", "tagline", "overview", "cast", "crew","release_date","runtime","vote_average"]]

    #Get unique dicts multi value cell column cells
    genre_dict = unique_dict_from_list_col(movies["genres"])
    cast_dict = unique_dict_from_list_col(movies["cast"])
    crew_dict = unique_dict_from_list_col(movies["crew"])

    #Add genres to database
    genre_objs=list()
    for genre in genre_dict.keys():
        obj=Genre(name=genre)
        genre_objs.append(obj)
        genre_dict[genre]=obj


    Genre.objects.bulk_create(genre_objs)
    Genre.objects.save()



    persona_objs=list()
    for person in cast_dict.keys():
        obj=Persona(full_name=person)
        persona_objs.append(obj)
        cast_dict[person]=obj

    for person in crew_dict.keys():
        obj=Persona(full_name=person)
        persona_objs.append(obj)
        crew_dict[person]=obj

    persona_objs.objects.save()

    # for rowID,movie in movies.iterrows():
    #
    #     pass
    # print("test")

fill_movies()


# def fill_database():
#     movies = pd.read(pd.read_csv("movies_metadata.csv.xz", encoding='utf8', infer_datetime_format=True))
#     movies['genres'] = movies['genres'].apply(onlygenrenames)
#     movies = movies[['id', 'title', 'genres', 'tagline', 'overview', 'cast', 'crew']]


# title = models.CharField(max_length=254)
# slug = models.SlugField(max_length=254, unique=True)
# length = models.FloatField(default=0.0, blank=True)
# released_on = models.DateField(blank=True, null=True)
# trailer = models.URLField(max_length=254, blank=True, default=None)
# plot = models.TextField(blank=True, null=True)
# # Relationships
# directors = models.ManyToManyField(Persona, related_name='directors')
# actors = models.ManyToManyField(Persona, related_name='actors')
# genres = models.ManyToManyField(Genre, related_name='genres')
# ratings = models.ManyToManyField(User, through='Rating', blank=True)
#
# created_at = models.DateTimeField(auto_now_add=True)
# updated_at = models.DateTimeField(auto_now=True)
