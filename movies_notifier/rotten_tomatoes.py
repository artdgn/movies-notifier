import re
import requests

from parsel import Selector

import movies_notifier.search
from movies_notifier.logger import logger


class RTScraper:

    allowed_missing_words = ['the']

    movie_page_url_patten = r'.*rottentomatoes.com/m/[^\/]*$'  # no slashes after /m/

    def __init__(self, movie_name, year, search_engine='g-cookies'):
        self.movie_name = movie_name
        self.year = year
        self.search_scraper = movies_notifier.search.Scraper(search_setting=search_engine)
        self.rt_url = None
        self.critics_rating = None
        self.audience_rating = None
        self.title = None
        self.synopsis = None
        self.error = None

    def _search_query(self):
        return f'{self.movie_name} {self.year} site:www.rottentomatoes.com'

    def get_ratings(self, check_title=True, stop_on_errors=True):
        try:
            self.get_rt_url_from_search()
            self.get_ratings_from_rt_url()
        except Exception as e:
            if stop_on_errors:
                raise e
            else:
                logger.exception(e)
                self.error = str(e)
        return self.format_results(check_title=check_title)

    @staticmethod
    def strip_punctuation(s):
        return re.sub(r'[^\w\s]', '', str(s)).lower()

    def _match_score(self, r_dict):
        results_title = self.strip_punctuation(r_dict['title'])
        input_title_parts = self.strip_punctuation(self.movie_name).split()
        score = 0
        if re.fullmatch(self.movie_page_url_patten, r_dict['link']) is not None:
            score += sum([w in results_title or w in self.allowed_missing_words
                 for w in input_title_parts])
        return score

    def get_rt_url_from_search(self):

        first_page_results = self.search_scraper.get_results(self._search_query())

        best_match = max(first_page_results, key=self._match_score)
        rt_url = best_match['link']

        if self._match_score(best_match) is 0:
            logger.warn(f"Couldn't find exact match in first page of "
                        f"search results for {self.movie_name}, "
                        f"trying first result as fallback")
            rt_url = first_page_results[0]['link']

        self.rt_url = rt_url

    def get_ratings_from_rt_url(self):
        resp = requests.get(self.rt_url)
        self._scrape_rt_response(resp)

    def _scrape_rt_response(self, resp):
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

