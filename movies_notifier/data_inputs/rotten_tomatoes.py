import json
import re
import requests

from parsel import Selector

from movies_notifier.data_inputs import search
from movies_notifier.util.logger import logger


class MovieRatingsScraper:

    allowed_missing_words = ['the']

    _movie_page_url_patten = r'.*rottentomatoes.com/m/[^\/]*$'  # no slashes after /m/

    _audience_api = 'https://www.rottentomatoes.com/napi/audienceScore/'

    def __init__(self, movie_name, year, search_engine='g', cookies='none'):
        self.movie_name = movie_name
        self.year = year
        self.search_scraper = search.Scraper(
            search_engine=search_engine, cookies=cookies)
        self.rt_url = None
        self.critics_rating = None
        self.critics_avg_score = None
        self.critics_n_reviews = None
        self.audience_rating = None
        self.audience_avg_score = None
        self.audience_n_reviews = None
        self.title = None
        self.synopsis = None
        self.error = None

    def _search_query(self):
        return f'{self.movie_name} {self.year} site:www.rottentomatoes.com'

    def get_ratings(self, check_title=True, raise_error=True):
        try:
            self.get_rt_url_from_search()
            self.get_ratings_from_rt_url()
        except Exception as e:
            if raise_error:
                logger.error(f'Raising and failing because raise_error={raise_error}')
                raise e
            else:
                logger.exception(e)
                self.error = str(e)
        return self.format_results(check_title=check_title)

    @staticmethod
    def normalise_title(s):
        return ' '.join(re.sub(r'[^\w\s]', '', str(s)).lower().split())

    def _url_check(self, url):
        return re.fullmatch(self._movie_page_url_patten, url) is not None

    def _title_similarity_score(self, candidate, target):
        cand_parts = self.normalise_title(candidate).split()
        target = self.normalise_title(target)
        if not cand_parts or not target:
            return 0
        score = sum([w in target or w in self.allowed_missing_words
                  for w in cand_parts])
        return score / len(target.split())

    def _match_search_result(self, r_dict):
        score = self._title_similarity_score(
            candidate=r_dict['title'], target=self.movie_name)
        if not self._url_check(r_dict['link']):
            score *= 0.75
        return score

    def get_rt_url_from_search(self):

        first_page_results = self.search_scraper.get_results(self._search_query())

        best_match = max(first_page_results, key=self._match_search_result)
        rt_url = best_match['link']

        if self._match_search_result(best_match) is 0:
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

        self.critics_data = self._get_full_critics_data(resp)
        self.critics_rating = self.critics_data.get(
            'tomatometerAllCritics', {}).get('score', '')
        self.critics_avg_score = self.critics_data.get(
            'tomatometerAllCritics', {}).get('avgScore', '')
        self.critics_n_reviews = self.critics_data.get(
            'tomatometerAllCritics', {}).get('numberOfReviews', '')

        if not self.critics_rating:  # try css
            self.critics_rating = sel.css(
                '#tomato_meter_link .mop-ratings-wrap__percentage::text').extract_first() or ''
            self.critics_rating = self.critics_rating.strip()[:-1]

        self.audience_data = self._get_full_audience_data(resp)
        self.audience_rating = self.audience_data.get(
            'audienceScoreAll', {}).get('score', '')
        self.audience_avg_score = self.audience_data.get(
            'audienceScoreAll', {}).get('averageRating', '')
        self.audience_n_reviews = self.audience_data.get(
            'audienceScoreAll', {}).get('reviewCount', '')

        self.title = self.critics_data.get(
            'tomatometerAllCritics', {}).get('title', '')
        if not self.title:  # try css
            self.title = sel.css('.mop-ratings-wrap__title--top::text').extract_first() or ''
            self.title = self.title.strip()

        # synopsis
        self.synopsis = sel.css('#movieSynopsis::text').extract_first() or ''
        self.synopsis = self.synopsis.strip()

    def _get_full_critics_data(self, resp):
        try:
            si_str = 'root.RottenTomatoes.context.scoreInfo'
            return json.loads(re.findall(f'{si_str} = (.*);', resp.text)[0])
        except (json.decoder.JSONDecodeError, TypeError, IndexError):
            logger.error('failed getting structured critics score data_inputs')
            return {}

    def _get_full_audience_data(self, resp):
        try:
            fd_str = 'root.RottenTomatoes.context.fandangoData'
            fd_dict = json.loads(re.findall(f'{fd_str} = (.*);', resp.text)[0])
            if fd_dict.get('emsId'):
                resp_aud = requests.get(self._audience_api + fd_dict['emsId'])
                return resp_aud.json()
            else:
                return {}
        except (IndexError, AttributeError, TypeError):
            return {}

    def format_results(self, check_title=True):
        res = {
            'rt_url': self.rt_url,
            'critics_rating': self.critics_rating,
            'critics_avg_score': self.critics_avg_score,
            'critics_n_reviews': self.critics_n_reviews,
            'audience_rating': self.audience_rating,
            'audience_avg_score': self.audience_avg_score,
            'audience_n_reviews': self.audience_n_reviews,
            'title': self.title,
        }

        if self.error:
            res['error'] = self.error

        if not self.error and check_title and \
                self._title_similarity_score(candidate=self.title, target=self.movie_name) <= 0.8:
            res['critics_rating'] = None
            res['critics_avg_score'] = None
            res['critics_n_reviews'] = None
            res['audience_rating'] = None
            res['audience_avg_score'] = None
            res['audience_n_reviews'] = None
            err_msg = f'RT title and input title are different: ' \
                      f'{self.normalise_title(self.title)} ' \
                      f'!= {self.normalise_title(self.movie_name)}'
            res['error'] = err_msg
            logger.error(err_msg)
        return res

