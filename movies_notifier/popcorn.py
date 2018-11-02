import requests
import time

from movies_notifier.common import CURRENT_DATE
from movies_notifier.logger import logger
from movies_notifier.rotten_tomatoes import RTScraper


class PopcornWithRT:

    POPCORN_API_URI = "https://tv-v2.api-fetch.website"

    @classmethod
    def get_popcorn_movies(cls, page, sort='last added'):
        movies = requests.get(f'{cls.POPCORN_API_URI}/movies/{page}',
                              params={'sort': sort, 'order': -1}).json()
        return movies

    @staticmethod
    def add_info_fields(m):
        m.update({
            'scrape_date': CURRENT_DATE,
            'magnet_1080p': m['torrents'].get('en', {}).get('1080p', {}).get('url'),
            'magnet_720p': m['torrents'].get('en', {}).get('720p', {}).get('url')
        })


    @classmethod
    def get_new_movies(cls, max_pages = 10, request_delay = 3,
                       skip_func=None, stop_on_stale_page=True):

        new_movies = {}  #using dict or deduplication as API sometimes returns duplicates

        for i in range(1, max_pages + 1):

            page_movies = cls.get_popcorn_movies(i)
            new_movies_on_page = 0

            for m in page_movies:
                m_id = m['_id']

                if skip_func is not None and skip_func(m_id):
                    continue

                new_movies_on_page += 1

                cls.add_info_fields(m)

                cls.add_rt_fields(m, scrape_delay=request_delay)

                new_movies[m_id] = m

            if stop_on_stale_page and not new_movies_on_page:
                break

            time.sleep(request_delay)

        logger.info(f'Got {len(new_movies)} new movies from popcorn API')

        return list(new_movies.values())

    @staticmethod
    def add_rt_fields(m, scrape_delay=3, overwrite=True):
        if overwrite or 'rotten_tomatoes' not in m:
            ratings = RTScraper(movie_name=m['title'], year=m['year']).get_ratings()
            m.update({'rotten_tomatoes': ratings})
            logger.info(f"Got {ratings} for {m['title']}")
            time.sleep(scrape_delay)




