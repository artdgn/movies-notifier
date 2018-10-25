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

        def movies_list():
            return list(new_movies.values())

        new_movies = {}  #using dict or deduplication as API sometimes returns duplicates

        for i in range(1, max_pages + 1):

            page_movies = cls.get_popcorn_movies(i)

            for m in page_movies:
                m_id = m['_id']

                if stop_func is not None and stop_func(m_id):
                    logger.info(f'Got {len(new_movies)} new movies from popcorn API')
                    return movies_list()

                cls.add_fields(m)
                new_movies[m_id] = m

            time.sleep(request_delay)

        if stop_func is not None:
            logger.warn('All movies in range were new, '
                        'either something is wrong or movie cache empty')

        return movies_list()




