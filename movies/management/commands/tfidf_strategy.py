from django.core.management.base import BaseCommand, CommandError
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from movies.models import Movie

class Command(BaseCommand):
    help = 'Movie based recommendation'

    def handle(self, *args, **options):
        primary_movie_id = Movie.objects.first().id
        getTfIdfRecommendations(primary_movie_id)

# ---------------------------------------------------------
# Content-Based recommendation system (Cognitive Filtering)
# ---------------------------------------------------------
# Term Frequency — Inverse Document Frequency
# ---------------------------------------------------------
def getTfIdfRecommendations(movie_id: int, cut_off: int = 5) -> pd.DataFrame:
    """TF-IDF score is the frequency of a word occurring in a document,
    down-weighted by the number of documents in which it occurs. This is done to reduce
    the importance of words that frequently occur in plot.

    Args:
        movie_id (int): id of the movie searched by the user.
        cut_off (int, optional): number of recommendations. Defaults to 5.

    Returns:
        pd.DataFrame: recommended movies ordered by relevance (score).
    """
    movies_df = pd.DataFrame.from_records(Movie.objects.all().values('id', 'title', 'slug', 'plot', 'poster_path'))

    movies_df['title'].fillna('', inplace=True)
    movies_df['plot'].fillna('', inplace=True)

    # Merging title, tagline and overview together in a new column
    movies_df['document'] = movies_df['title'] + ' ' + movies_df['plot']
    
    primary_movie = getMovie(movies_df, movie_id)

    # Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a', etc.
    tf: TfidfVectorizer = TfidfVectorizer(stop_words='english')

    # Generate a matrix having |movies| rows and each word in the overviews is a column.
    # movies_df['document']: collection of documents.
    tfidf_matrix = tf.fit_transform(movies_df['document'])
    # print('Movies: ', tfidf_matrix.shape[0], ' - Columns (words): ', tfidf_matrix.shape[1])

    primary_overview_tfidf_matrix = tf.transform(primary_movie['document'].values)
    # Create the cosine similarity matrix
    sim_matrix = cosine_similarity(primary_overview_tfidf_matrix, tfidf_matrix).flatten()
    movies_df.insert(movies_df.shape[1], 'score', sim_matrix, allow_duplicates=True)
    recommendations = movies_df.sort_values(by=['score'], ascending=False)[['id', 'title', 'slug', 'poster_path', 'score']]
    pd.set_option('display.max_columns', None)
    print(recommendations[1:cut_off+1])

def getMovie(movies: pd.DataFrame, movie_id: int) -> pd.DataFrame:
    """Return movie record in the dataframe.

    Args:
        movies (pd.DataFrame): dataframe containing all the movies.
        movie_id (str): id of the movie searched by the user.

    Raises:
        Exception: movie not found exception if movie is not found.

    Returns:
        pd.DataFrame: searched movie as dataframe.
    """
    movie = movies[movies['id'] == movie_id]
    if (movie.empty):
        print('Movie {} not found'.format(movie_id))
        raise Exception('Movie {} id not found'.format(movie_id))

    return movie

# docker exec django-container python manage.py tfidf_strategy
