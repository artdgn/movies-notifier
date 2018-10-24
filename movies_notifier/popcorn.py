import requests
import time

from movies_notifier.common import CURRENT_DATE
from movies_notifier.logger import logger


class PopcornClient:

    POPCORN_API_URI = "https://tv-v2.api-fetch.website"

    @classmethod
    def get_popcorn_movies(cls, page, sort='last added'):
        movies = requests.get(cls.POPCORN_API_URI + f'/movies/{page}',
                              params={'sort': sort, 'order': -1}).json()
        return movies

    @staticmethod
    def add_fields(m):
        m.update({
            'scrape_date': CURRENT_DATE,
            'magnet_1080p': m['torrents'].get('en', {}).get('1080p', {}).get('url'),
            'magnet_720p': m['torrents'].get('en', {}).get('720p', {}).get('url')
        })

    @classmethod
    def get_new_movies(cls, max_pages = 10, request_delay = 3, stop_func=None):
        new_movies = []
        for i in range(1, max_pages):
            page_movies = cls.get_popcorn_movies(i)
            for m in page_movies:
                if stop_func is not None and stop_func(m['_id']):
                    logger.info(f'Got {len(new_movies)} new movies from popcorn API')
                    return new_movies
                else:
                # if not MoviesStore.exists(m['_id']):
                    cls.add_fields(m)
                    new_movies.append(m)
            time.sleep(request_delay)
        logger.warn('All movies in range were new, '
                    'either something is wrong or movie cache empty')
        return new_movies




