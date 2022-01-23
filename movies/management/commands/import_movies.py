from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from pathlib import Path
import pandas as pd
import os
from tqdm import tqdm
import logging
from slugify import slugify
import itertools

from movies.models import Genre, Movie, Persona

#TODO: Discuss, how and when logger should be used
logger = logging.getLogger('command_import_movies')

class Command(BaseCommand):

    help = 'Import movies and the main relationships'

    def str_dict_to_list(self,genres)->list[str]:
        genre_aslist = eval(genres)
        return [g["name"] for g in genre_aslist]

    def str_dict_to_director_list(self,genres)->list[str]:
        genre_aslist = eval(genres)
        return [g["name"] for g in genre_aslist if g["department"] == "Directing"]

    def unique_dict_from_list_col(self,list_col)->list[str]:
        return dict.fromkeys(itertools.chain.from_iterable(list_col), None)
        # unique_dict=dict()
        # i=0
        # for val in unique_values:
        #     unique_dict[val]=i
        #     i+=1

        #return unique_dict

    def handle(self, *args, **kwargs):
        # # This will break as Docker does not see files in the local machine.
        #TODO: add user path and more error handling later

        # movies_path = Path(os.getenv('MOVIES_PATH')).expanduser()

        logger.info('Import started')

        self.fill_movies()

        logger.info('Import completed')
        self.stdout.write(self.style.SUCCESS('Import completed'))

    #Fills EMTPY Movie database
    def fill_movies(self)->None:
        # Get movies dataframe

        filePath=Path(__file__).parent.resolve()
        moviePath = os.path.join(filePath, "movies_metadata.csv.xz")
        creditsPath = os.path.join(filePath, "credits.csv.xz")

        movies=self.get_movies_df(moviePath,creditsPath)

        # Get unique dicts multi value cell column cells
        genres = self.unique_dict_from_list_col(movies["genres"])
        casts = self.unique_dict_from_list_col(movies["cast"])
        crews = self.unique_dict_from_list_col(movies["crew"])

        self.assign_genre_objects(genres)
        self.assign_persona_objetcs(casts,crews)

        self.add_genre_elements_to_db(list(genres.values()))
        self.add_persona_elements_to_db(list(casts.values()),list(crews.values()))

        movie_objects=self.create_movie_objects(movies,genres,casts,crews)


        self.add_movies_to_db(movie_objects)

        #Genre.objects.save()

    def add_movies_to_db(self,movies:list[Movie]):
        try:
            Movie.objects.bulk_create(movies)
        except IntegrityError:
            logger.warning("Tried to insert values into movies that are already there")

    def create_movie_objects(self,movies:pd.DataFrame,genres:dict[str,Genre],casts:[str,Genre],crews:[str,Genre])->list[Movie]:
        #TODO: add ratings and trailer later
        movie_objects=list()
        for index,row in movies.iterrows():
            #TODO: add trailer later

            genre_objs=list()
            actor_objs=list()
            director_objs=list()

            for genre in row["genres"]:
                genre_objs.append(genres[genre])
            for director in row["crew"]:
                director_objs.append(crews[director])
            for actor in row["cast"]:
                actor_objs.append(casts[actor])

            movie=Movie(title=row["title"],slug=slugify(row["title"]),length=row["runtime"],released_on=row["release_date"],trailer="",plot=row["overview"],directors=director_objs,actors=actor_objs,genres=genre_objs,ratings=None)
            movie_objects.append()
        return movie_objects


    def get_movies_df(self,moviePath,creditsPath)->pd.DataFrame:
        movies = pd.read_csv(moviePath, encoding="utf8", infer_datetime_format=True)
        movies["genres"] = movies["genres"].apply(self.str_dict_to_list)

        # get credits dataframe (more info on cast/directors)
        credits = pd.read_csv(creditsPath, encoding="utf8")

        # merge information
        movies = pd.merge(movies, credits, on="id")

        movies["cast"] = movies["cast"].apply(self.str_dict_to_list)
        movies["crew"] = movies["crew"].apply(self.str_dict_to_director_list)
        return movies[["id", "title", "genres", "tagline", "overview", "cast", "crew", "release_date", "runtime", "vote_average"]]

    def assign_genre_objects(self,genres:dict[str,Genre])->None:
        # Add genres to database
        genre_objs = list()
        for genre in genres.keys():
            obj = Genre(name=genre,slug=slugify(genre))
            genre_objs.append(obj)
            genres[genre] = obj

    def add_genre_elements_to_db(self,genres:list[Genre])->None:
        try:
            Genre.objects.bulk_create(genres)
        except IntegrityError:
            logger.warning("Tried to insert values into genre that are already there")
    def add_persona_elements_to_db(self,casts:list[Persona],crews:list[Persona])->None:
        try:
            Persona.objects.bulk_create(casts+crews)
        except IntegrityError:
            logger.warning("Tried to insert values into personas that are already there")

    def assign_persona_objetcs(self,casts:dict[str,Persona],crews:dict[str,Persona])->None:
        persona_objs=list()
        for person in casts.keys():
            obj = Persona(full_name=person)
            persona_objs.append(obj)
            casts[person] = obj

        for person in crews.keys():
            obj = Persona(full_name=person)
            persona_objs.append(obj)
            crews[person] = obj


# python manage.py import_movies



