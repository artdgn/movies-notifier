import json
import os
import time

import pandas as pd

from movies_notifier.logger import logger
from movies_notifier.popcorn import PopcornClient
from movies_notifier.common import CURRENT_DATE, MOVIES_DIR
from movies_notifier.rotten_tomatoes import RTScraper


class MoviesStore:

    def __init__(self):
        self.movies = []
        self.new_movies = []

    @staticmethod
    def add_rt_fields(movies, scrape_delay=3, overwrite=True):
        for m in movies:
            if overwrite or 'rotten_tomatoes' not in m:
                ratings = RTScraper(movie_name=m['title'], year=m['year']).get_ratings()
                m.update({'rotten_tomatoes': ratings})
                logger.info(f"Got {ratings} for {m['title']}")
                time.sleep(scrape_delay)
        return movies

    @staticmethod
    def movie_json_path(_id):
        filename = _id + '.json'
        return os.path.join(MOVIES_DIR, filename)

    @classmethod
    def exists(cls, _id):
        return os.path.exists(cls.movie_json_path(_id))

    def save_movies(self, movies, overwrite=False):
        for m in movies:
            filepath = self.movie_json_path(m['_id'])
            if overwrite or not os.path.exists(filepath):
                with open(filepath, 'wt') as f:
                    json.dump(m, f)
                logger.info(f"Saved {m['_id']} ({m['title']})")

    def load_movies(self):
        files = os.listdir(MOVIES_DIR)
        for filename in files:
            filepath = os.path.join(MOVIES_DIR, filename)
            with open(filepath, 'rt') as f:
                try:
                    self.movies.append(json.load(f))
                except Exception as e:
                    logger.error(f'Failed json read for {filepath}')

    def delete_too_old(self, days_diff = 60):
        def too_old(date):
            return (pd.to_datetime(CURRENT_DATE) - pd.to_datetime(date)) > \
                   pd.to_timedelta(f'{days_diff} days')

        for m in self.movies:
            if too_old(m['scrape_date']):
                os.remove(self.movie_json_path(m['_id']))
                logger.info(f"Removing {m['_id']} because "
                            f"{m['scrape_date']} is more than {days_diff} old")

    def get_new_movies(self, max_pages=10):
        self.new_movies = PopcornClient.\
            get_new_movies(max_pages=max_pages, stop_func=self.exists)
        self.add_rt_fields(self.new_movies)
        self.save_movies(self.new_movies)
        # self.delete_too_old()
        return self.new_movies

    @staticmethod
    def select_good_movies(new_movies, critics_threshold=80, audience_threshold=80):
        good_movies = []
        for m in new_movies:
            rt_data = m['rotten_tomatoes']
            if \
                    rt_data['critics_rating'] and \
                    int(rt_data['critics_rating']) > critics_threshold and \
                    rt_data['audience_rating'] and \
                    int(rt_data['audience_rating']) > audience_threshold:
                good_movies.append(m)
        logger.info(f'Selected {len(good_movies)} good movies from {len(new_movies)} new movies')
        return good_movies

    @staticmethod
    def remove_fields(movies, keep_keys=None):
        if keep_keys is None:
            keep_keys = ['_id', 'genres', 'rotten_tomatoes',
                         'title', 'year', 'magnet_1080p', 'magnet_720p']
        return [{k: d[k] for k in keep_keys} for d in movies]