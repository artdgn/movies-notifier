import json
import os

import pandas as pd

from movies_notifier.config import common
from movies_notifier.util import pandas_utils
from movies_notifier.util.logger import logger


class Movie(dict):

    def json_path(self, dir):
        return os.path.join(dir, f"{self['_id']}.json")

    def load_from_disk(self, dir):
        path = self.json_path(dir)
        if os.path.exists(path):
            with open(path, 'rt') as f:
                m = json.load(f)
                self.update(m)
                return True

    def rt_data(self):
        return self.get('rotten_tomatoes')

    @staticmethod
    def adjust_score(score, n_reviews, precision=1):
        try:
            # rule of succession for binary (success / failure)
            raw = float(score)
            n = float(n_reviews)
            adjusted = 100 * ((raw * n / 100) + 1) / (n + 2)
            return round(adjusted, precision)
        except ValueError:
            return score

    def rt_critics_rating(self, min_n_reviews=0, adjust_by_n_reviews=True):
        if (not self.rt_critics_n_reviews() or
                self.rt_critics_n_reviews() >= min_n_reviews):
            if not adjust_by_n_reviews or not self.rt_critics_n_reviews():
                return self.rt_critics_rating_raw()
            else:
                return self.adjust_score(self.rt_critics_rating_raw(),
                                         self.rt_critics_n_reviews())

    def rt_critics_rating_raw(self):
        return self.get('rotten_tomatoes', {}).get('critics_rating')

    def rt_critics_avg_score(self):
        return self.get('rotten_tomatoes', {}).get('critics_avg_score')

    def rt_critics_n_reviews(self):
        return self.get('rotten_tomatoes', {}).get('critics_n_reviews')

    def rt_audience_rating(self, min_n_reviews=0, adjust_by_n_reviews=True):
        if (not self.rt_audience_n_reviews() or
                self.rt_audience_n_reviews() >= min_n_reviews):
            if not adjust_by_n_reviews or not self.rt_audience_n_reviews():
                return self.rt_audience_rating_raw()
            else:
                return self.adjust_score(self.rt_audience_rating_raw(),
                                         self.rt_audience_n_reviews())

    def rt_audience_rating_raw(self):
        return self.get('rotten_tomatoes', {}).get('audience_rating')

    def rt_audience_avg_score(self):
        return self.get('rotten_tomatoes', {}).get('audience_avg_score')

    def rt_audience_n_reviews(self):
        return self.get('rotten_tomatoes', {}).get('audience_n_reviews')

    def id(self):
        return self['_id']

    def title(self):
        return self['title']

    def minimal_fields(self, keep_keys=None):
        if keep_keys is None:
            keep_keys = ['title', 'year', 'genres', 'rotten_tomatoes']
            keep_keys.append('magnet_1080p'
                             if self.get('magnet_1080p') else 'magnet_720p')
            keep_keys.append('_id')

        return Movie({k: self[k] for k in keep_keys if k in self})


class MoviesStore:

    def __init__(self):
        self.movies = {}
        self.load_movies()

    @staticmethod
    def movie_json_path(m):
        return Movie(m).json_path(common.MOVIES_DIR)

    @classmethod
    def exists(cls, m):
        return os.path.exists(cls.movie_json_path(m))

    @classmethod
    def has_rt_data(cls, m):
        movie = Movie(m)
        if movie.load_from_disk(common.MOVIES_DIR):
            return (movie.rt_critics_rating() or
                    movie.rt_audience_rating() or
                    movie.rt_critics_avg_score())
        return False

    def save_movies(self, overwrite=False):
        [self.save_movie(m, overwrite=overwrite) for m in self.movies.values()]

    def save_movie(self, m, overwrite=False):
        filepath = self.movie_json_path(m)
        if overwrite or not os.path.exists(filepath):
            with open(filepath, 'wt') as f:
                json.dump(m, f)
            logger.info(f"Saved {m.id()} ({m.title()})")

    def add_movies(self, movies, save=True, overwrite=False):
        [self.add_movie(m, save=save, overwrite=overwrite) for m in movies]

    def add_movie(self, movie_dict, save=True, overwrite=False):
        m = Movie(movie_dict)
        self.movies[m.id()] = m
        if save:
            self.save_movie(m, overwrite=overwrite)

    def load_movies(self):
        files = os.listdir(common.MOVIES_DIR)
        for filename in files:
            filepath = os.path.join(common.MOVIES_DIR, filename)
            with open(filepath, 'rt') as f:
                try:
                    self.add_movie(json.load(f))
                except Exception as e:
                    logger.error(f'Failed json read for {filepath}')

    def movies_df(self):
        if not self.movies:
            self.load_movies()
        return self.movie_list_to_export_df(list(self.movies.values()))

    @staticmethod
    def movie_list_to_export_df(movie_list, adjust_scores=True):
        df = pd.DataFrame(movie_list)

        # expand rt data
        df['rotten_tomatoes'] = df['rotten_tomatoes'].apply(json.dumps)
        df = pandas_utils.split_json_field(df, 'rotten_tomatoes')
        df = df.iloc[:, ~df.columns.duplicated()]  # json split creates duplicate title

        # process numeric
        score_cols = ['critics_rating', 'critics_avg_score', 'critics_n_reviews',
                      'audience_rating', 'audience_avg_score', 'audience_n_reviews']
        score_cols = [c for c in score_cols if c in df.columns]
        df.loc[:, score_cols] = df.loc[:, score_cols].apply(pd.to_numeric)

        if adjust_scores:
            df['critics_rating'] = df.apply(
                lambda r: Movie.adjust_score(r['critics_rating'],
                                             r['critics_n_reviews'] or 1000  # no adjustment if missing
                                             ), axis=1)
            df['audience_rating'] = df.apply(
                lambda r: Movie.adjust_score(r['audience_rating'],
                                             r['audience_n_reviews'] or 1000  # no adjustment if missing
                                             ), axis=1)

        df['mean_score'] = (df['audience_rating'] + df['critics_rating']) / 2
        df_sort = df.sort_values('mean_score', ascending=False)

        # sort columns and rows
        cols_order = (['title', 'year', 'genres'] + score_cols +
                      ['rt_url', 'magnet_1080p', 'magnet_720p',
                       'error', 'scrape_date'])
        cols_order = [c for c in cols_order if c in df.columns]
        return df_sort[cols_order]

    @classmethod
    def write_html_table_for_list(cls, movies_list):
        filename = os.path.join(common.HTML_DIR,
                                f'table_{common.CURRENT_TIMESTAMP}.html')
        df = cls.movie_list_to_export_df(movies_list)
        with open(filename, 'wt') as f:
            f.write(df.to_html(index=None, escape=False, render_links=True))
        logger.info(f'movies list saved to table at: {filename}')
