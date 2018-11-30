import re
import requests

from parsel import Selector

from movies_notifier.google_search import get_first_page_google_results
from movies_notifier.logger import logger


class RTScraper:

    def __init__(self, movie_name, year):
        self.movie_name = movie_name
        self.year = year
        self.rt_url = None
        self.critics_rating = None
        self.audience_rating = None
        self.title = None
        self.synopsis = None
        self.error = None

    def get_ratings(self, check_title=True):
        try:
            self.get_rt_url_from_google()
            self.get_ratings_from_rt_url()
        except Exception as e:
            logger.exception(e)
            self.error = str(e)
        return self.format_results(check_title=check_title)

    @staticmethod
    def strip_punctuation(s):
        return re.sub(r'[^\w\s]', '', str(s)).lower()

    def get_rt_url_from_google(self, check_title=True):

        first_page_results = get_first_page_google_results(
            f'movie {self.movie_name} rotten tomatoes {self.year}')

        rt_url = None

        if check_title:
            for r_dict in first_page_results:
                google_title = self.strip_punctuation(r_dict['title'])
                input_title_parts = self.strip_punctuation(self.movie_name).split()
                if all([w in google_title for w in input_title_parts]) \
                        and 'rottentomatoes.com/m/' in r_dict['link']:
                   rt_url = r_dict['link']

        if rt_url is None:
            if check_title:
                logger.warn(f"Couldn't find exact match in first page of "
                            f"google results for {self.movie_name}, "
                            f"trying first result as fallback")
            rt_url = first_page_results[0]['link']

        self.rt_url = rt_url

    def get_ratings_from_rt_url(self):
        resp = requests.get(self.rt_url)

        sel = Selector(text=resp.text)

        # critics
        self.critics_rating = sel.css('#tomato_meter_link '
                               '.superPageFontColor span::text').extract_first() or ''
        # audience
        self.audience_rating = sel.css('.meter-value '
                                '.superPageFontColor::text').extract_first() or ''
        self.audience_rating = self.audience_rating[:-1]

        # title (to make sure we have the right movie)
        self.title = sel.css('#movie-title::text').extract_first() or ''
        self.title = self.title.strip()

        # synopsis
        self.synopsis = sel.css('#movieSynopsis::text').extract_first() or ''
        self.synopsis = self.synopsis.strip()

    def format_results(self, check_title=True):
        res = {
            'rt_url': self.rt_url,
            'critics_rating': self.critics_rating,
            'audience_rating': self.audience_rating,
            'title': self.title,
            # 'synopsis': self.synopsis
        }

        if self.error:
            res['error'] = self.error

        if not self.error and check_title \
                and self.strip_punctuation(self.movie_name) \
                not in self.strip_punctuation(self.title):
            res['critics_rating'] = None
            res['audience_rating'] = None
            err_msg = f'RT title and input title are different: ' \
                      f'{self.strip_punctuation(self.title)} ' \
                      f'!= {self.strip_punctuation(self.movie_name)}'
            res['error'] = err_msg
            logger.error(err_msg)
        return res

