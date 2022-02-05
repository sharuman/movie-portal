import os
from pathlib import Path

import numpy as np
import pandas as pd

class DataFrameReader:
    def __init__(self):
        self.movies_path = Path(os.getenv('MOVIES_PATH')).expanduser()
        self.credits_path = Path(os.getenv('CREDITS_PATH')).expanduser()
        self.ratings_path = Path(os.getenv('RATINGS_PATH')).expanduser()

        # logger.info('Import started')
        # self.stdout.write(self.style.NOTICE('Import started'))



    def get_movies_df(self,max_rows:int) -> pd.DataFrame:
        movies = pd.read_csv(
            self.movies_path,
            usecols=['id', 'title', 'genres', 'overview', 'tagline', 'release_date', 'runtime'],
            low_memory=False,
            encoding="utf8",
            infer_datetime_format=True)

        movies["id"].apply(
            self.convert_to_int_or_nan)  # The ids of the dataset are not clean (non numbers inside), so we actually have to get them into a proper format
        movies.dropna(inplace=True)  # Drop all rows that have na values that matter to us -> Also invalid id rows
        movies = movies.astype({'id': np.int64},
                               copy=False)  # Now we can set the column to the proper type without getting an error because the conversion doesn't work

        if max_rows > 0:
            movies = movies.head(max_rows)  # Get first 1000 rows

        # get credits dataframe (more info on cast/directors)
        credits_df = pd.read_csv(self.credits_path,
                                 encoding="utf8")  # We don't call it credits, because it is already a built in function
        credits_df.dropna(inplace=True)  # Drop all rows that have na values that matter to us

        movies = pd.merge(movies, credits_df, on="id")  # Match the two dataframes on id

        # Convert from a string representation of a dict to an actual list
        movies["genres"] = movies["genres"].apply(self.str_dict_to_dict)
        movies["cast"] = movies["cast"].apply(self.str_dict_to_dict)
        movies["crew"] = movies["crew"].apply(self.str_dict_to_director_dict)

        movies = movies[["id", "title", "genres", "tagline", "overview", "cast", "crew", "release_date", "runtime"]]
        movies.drop_duplicates(subset=["id"], inplace=True)  # Only keep merged rows where everything is there
        return movies

    def get_ratings_df(self,max_rows:int) -> pd.DataFrame:
        ratings = pd.read_csv(
            self.ratings_path,
            usecols=['userId', 'movieId', 'rating'],
            dtype={"userId": np.int64, "movieId": np.int64},
            low_memory=False,
            encoding="utf8",
            infer_datetime_format=True)
        if max_rows > 0:
            ratings = ratings.head(max_rows)  # Get first 1000 rows
        return ratings

        # |---------------------------------------------------------------
        # | Helper functions
        # |---------------------------------------------------------------

    def str_dict_to_dict(self, str_dict) -> dict[int, str]:
        genre_aslist = eval(str_dict)
        all_entries = dict()

        for g in genre_aslist:
            all_entries[g["id"]] = g["name"]

        return all_entries

    def str_dict_to_director_dict(self, str_dict) -> dict[int, str]:
        genre_aslist = eval(str_dict)
        all_entries = dict()
        for g in genre_aslist:
            if g["department"] == "Directing":
                all_entries[g["id"]] = g["name"]

        return all_entries

    def dict_from_dict_col(self, dict_col) -> dict[int, str]:
        unique_dict = dict()
        for row_dict in dict_col.values:
            for id, name in row_dict.items():
                unique_dict[id] = name

        return unique_dict

    def convert_to_int_or_nan(self, val: str):  # Either return an int, or if this is not possible, a nan value
        try:
            return int(val)
        except ValueError:
            return np.nan

