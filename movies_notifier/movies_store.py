import json
import os

import pandas as pd

from movies_notifier import pandas_utils
from movies_notifier.logger import logger
from movies_notifier.common import CURRENT_DATE, MOVIES_DIR


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

    def rt_critics(self):
        return self.get('rotten_tomatoes', {}).get('critics_rating')

    def rt_audience(self):
        return self.get('rotten_tomatoes', {}).get('audience_rating')

    def id(self):
        return self['_id']

    def title(self):
        return self['title']

    def to_dict(self):
        return dict(self)

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
        return Movie(m).json_path(MOVIES_DIR)

    @classmethod
    def exists(cls, m):
        return os.path.exists(cls.movie_json_path(m))

    @classmethod
    def has_full_rt_data(cls, m):
        movie = Movie(m)
        if movie.load_from_disk(MOVIES_DIR):
            return movie.rt_critics() is not None and \
                   movie.rt_audience() is not None
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
        files = os.listdir(MOVIES_DIR)
        for filename in files:
            filepath = os.path.join(MOVIES_DIR, filename)
            with open(filepath, 'rt') as f:
                try:
                    self.add_movie(json.load(f))
                except Exception as e:
                    logger.error(f'Failed json read for {filepath}')

    def delete_too_old(self, days_diff = 60):
        def too_old(date):
            return (pd.to_datetime(CURRENT_DATE) - pd.to_datetime(date)) > \
                   pd.to_timedelta(f'{days_diff} days')

        for m in self.movies.values():
            if too_old(m['scrape_date']):
                os.remove(self.movie_json_path(m))
                logger.info(f"Removing {m.id()} because "
                            f"{m['scrape_date']} is more than {days_diff} old")

    def movies_df(self):
        if not self.movies:
            self.load_movies()
        return self.movie_list_to_export_df(list(self.movies.values()))

    @staticmethod
    def movie_list_to_export_df(movie_list):
        df = pd.DataFrame(movie_list)
        df['rotten_tomatoes'] = df['rotten_tomatoes'].apply(json.dumps)
        df = pandas_utils.split_json_field(df, 'rotten_tomatoes')
        df = df.iloc[:, ~df.columns.duplicated()]  # json split creates duplicate title
        cols_order = ['title', 'year', 'genres', 'critics_rating', 'audience_rating',
                      'rt_url', 'magnet_1080p', 'magnet_720p', 'error', 'scrape_date']
        return df.loc[:, cols_order]

    @staticmethod
    def movie_df_to_html_table(df):
        linkifier = lambda link_text: lambda l: \
            f'<a href="{l}" target="_blank">{link_text}</a>'
        for col in ['rt_url', 'magnet_720p', 'magnet_1080p']:
            df[col] = df[col].apply(linkifier(col))

        pd.set_option('display.max_colwidth', -1)  # to prevent long links from getting truncated
        return df.to_html(index=None, escape=False)

