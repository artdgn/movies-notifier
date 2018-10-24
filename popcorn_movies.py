import os
import datetime
import requests
import json
import time
from pprint import pprint
import pandas as pd

from logger import logger

from rotten_tomatoes import RTScraper

CURRENT_DATE = datetime.datetime.now().date().isoformat()

MOVIES_DIR = './data/movies'
os.makedirs(MOVIES_DIR, exist_ok=True)


class PopcornClient:

    POPCORN_API_URI = "https://tv-v2.api-fetch.website"

    @classmethod
    def get_popcorn_movies(cls, page, sort='last added'):
        movies = requests.get(cls.POPCORN_API_URI + f'/movies/{page}',
                              params={'sort': sort, 'order': -1}).json()
        return movies

    @classmethod
    def get_new_movies(cls, max_pages = 10, request_delay = 3):
        new_movies = []
        for i in range(1, max_pages):
            page_movies = cls.get_popcorn_movies(i)
            for m in page_movies:
                if not MoviesStore.exists(m['_id']):
                    m.update({'scrape_date': CURRENT_DATE})
                    new_movies.append(m)
                else:
                    logger.info(f'Got {len(new_movies)} new movies from popcorn API')
                    return new_movies
            time.sleep(request_delay)
        logger.info('All movies in range were new, '
              'either something is wrong or movie cache empty')
        return new_movies


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

    def get_new_movies(self, max_pages=3):
        self.new_movies = PopcornClient.get_new_movies(max_pages=max_pages)
        self.add_rt_fields(self.new_movies)
        self.save_movies(self.new_movies)
        # self.delete_too_old()
        return self.new_movies




