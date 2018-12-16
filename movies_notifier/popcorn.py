import math
import random

import requests
import time

from movies_notifier.common import CURRENT_DATE
from movies_notifier.logger import logger
from movies_notifier.rotten_tomatoes import RTScraper


class PopcornWithRT:

    POPCORN_API_URI = "https://tv-v2.api-fetch.website"

    N_MOVIES_PAGE = 50

    sort_map = {'l': 'last added',
                'p': 'pupularity',
                't': 'trending'}

    def __init__(self, request_delay_range='5-30', stop_on_errors=True):
        self.request_delay_range = [int(s) for s in request_delay_range.split('-')]
        self.stop_on_errors = stop_on_errors

    @classmethod
    def _sort_param(cls, sort_str):
        sort_str = sort_str.strip()
        if sort_str in cls.sort_map.values():
            return sort_str
        elif sort_str in cls.sort_map:
            return cls.sort_map[sort_str]
        else:
            raise ValueError(f'Unknown value for sort type: {sort_str}')

    @classmethod
    def get_popcorn_movies(cls, page, sort='last added'):
        resp = requests.get(f'{cls.POPCORN_API_URI}/movies/{page}',
                              params={'sort': cls._sort_param(sort), 'order': -1})
        if resp.ok:
            movies = resp.json()
        else:
            logger.error(f'Failed getting {page} from Popcorn: {resp}')
            movies = []
        return movies

    @staticmethod
    def add_info_fields(m, page=None, index=None):
        m.update({
            'scrape_date': CURRENT_DATE,
            'scrape_page': page,
            'scrape_index_on_page': index,
            'magnet_1080p': m['torrents'].get('en', {}).get('1080p', {}).get('url'),
            'magnet_720p': m['torrents'].get('en', {}).get('720p', {}).get('url')
        })


    def get_new_movies(self,
                       movies_offset_range = (1, 100),
                       skip_func=None,
                       sort='l',
                       stop_on_stale_page=True,
                       save_func=None):

        new_movies = {}  #using dict or deduplication as API sometimes returns duplicates

        start_page = math.floor(movies_offset_range[0] / self.N_MOVIES_PAGE) + 1
        end_page = math.ceil(movies_offset_range[1] / self.N_MOVIES_PAGE)

        in_offset_range = lambda i, j: \
            movies_offset_range[0] <= ((i - 1) * self.N_MOVIES_PAGE + j + 1) <= movies_offset_range[1]

        for i in range(start_page, end_page + 1):

            page_movies = self.get_popcorn_movies(i, sort=sort)
            new_movies_on_page = 0

            for j, m in enumerate(page_movies):

                if skip_func is not None and skip_func(m):
                    logger.info(f"Skipping: {m['title']}")
                    continue

                new_movies_on_page += 1

                if in_offset_range(i, j):

                    self.add_info_fields(m, page=i, index=j)

                    self.add_rt_fields(m)

                    new_movies[m['_id']] = m

                    if save_func is not None:
                        save_func(m)

            if stop_on_stale_page and not new_movies_on_page:
                break

            self.request_delay()

        logger.info(f'Got {len(new_movies)} new movies from popcorn API')

        return list(new_movies.values())

    def add_rt_fields(self, m, overwrite=True):
        if overwrite or 'rotten_tomatoes' not in m:
            ratings = RTScraper(
                movie_name=m['title'], year=m['year']).\
                get_ratings(stop_on_errors=self.stop_on_errors)
            m.update({'rotten_tomatoes': ratings})
            logger.info(f"Got {ratings} for {m['title']}")
            self.request_delay()

    def request_delay(self):
        time.sleep(random.randint(*self.request_delay_range))




