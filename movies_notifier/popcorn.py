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
                't': 'trending',
                'y': 'year',
                'r': 'rating',
                }

    def __init__(self,
                 request_delay_range='5-30',
                 number_fails_threshold=3,
                 search_engine='g',
                 cookies=None,
                 ):
        self.request_delay_range = [int(s) for s in request_delay_range.split('-')]
        self.number_fails_threshold = number_fails_threshold
        self.search_engine = search_engine
        self.cookies = cookies
        self.n_consequtive_fails = 0

    @classmethod
    def _sort_param(cls, sort_str):
        sort_str = sort_str.strip()
        if sort_str in cls.sort_map.values():
            # full string option
            return sort_str
        elif sort_str in cls.sort_map:
            # abbreviated option
            return cls.sort_map[sort_str]
        else:
            raise ValueError(f'Unknown value for sort type: {sort_str}')

    @classmethod
    def _sorts_from_str(cls, sort_str):
        sort_str = sort_str.strip()

        if sort_str == 'all':
            sort_str = ''.join(cls.sort_map.keys())

        if all([c in cls.sort_map for c in sort_str]):
            # concatenation of several options
            return [cls._sort_param(c) for c in sort_str]
        else:
            return [cls._sort_param(sort_str)]

    @classmethod
    def get_popcorn_movies(cls, page, sort='last added'):
        resp = requests.get(f'{cls.POPCORN_API_URI}/movies/{page}',
                              params={'sort': cls._sort_param(sort), 'order': -1})
        if resp.ok:
            logger.info(f'Got page {page} from Popcorn for '
                        f'sort={cls._sort_param(sort)}')
            movies = resp.json()
        else:
            logger.error(f'Failed getting {page} from Popcorn '
                         f'for sort={cls._sort_param(sort)}: {resp}')
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

        new_movies = {}
        for s in self._sorts_from_str(sort_str=sort):
            new_movies.update(self._new_movies_for_sort(
                sort=s,
                movies_offset_range=movies_offset_range,
                skip_func=skip_func,
                stop_on_stale_page=stop_on_stale_page,
                save_func=save_func))
        return list(new_movies.values())

    def _new_movies_for_sort(self,
                            movies_offset_range = (1, 100),
                            skip_func=None,
                            sort='l',
                            stop_on_stale_page=True,
                            save_func=None):

        new_movies = {}  # using dict for deduplication as API sometimes returns duplicates

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

                    self.request_delay()

            if stop_on_stale_page and not new_movies_on_page:
                break

            self.request_delay()

        logger.info(f'Got {len(new_movies)} new movies from popcorn API')

        return new_movies

    def add_rt_fields(self, m, overwrite=True):
        if overwrite or 'rotten_tomatoes' not in m:
            rts = RTScraper(
                movie_name=m['title'],
                year=m['year'],
                search_engine=self.search_engine,
                cookies=self.cookies
            )
            ratings  = rts.get_ratings(
                raise_error=(self.n_consequtive_fails
                             >= self.number_fails_threshold))

            if not ratings or ratings.get('error'):
                self.n_consequtive_fails += 1
            else:
                self.n_consequtive_fails = 0

            m.update({'rotten_tomatoes': ratings})
            logger.info(f"Got {ratings} for {m['title']}")

    def request_delay(self):
        time.sleep(random.randint(*self.request_delay_range))




