import json
import re
import requests

from parsel import Selector

from movies_notifier.util.logger import logger


class MovieRatingsScraper:

    _base_url = 'https://www.rottentomatoes.com'

    _search_api = _base_url + '/api/private/v2.0/search'

    _audience_api = _base_url + '/napi/audienceScore/'

    def __init__(self, movie_name, year):
        self.movie_name = movie_name
        self.year = year
        self.rt_url = None
        self.critics_rating = None
        self.critics_avg_score = None
        self.critics_n_reviews = None
        self.audience_rating = None
        self.audience_avg_score = None
        self.audience_n_reviews = None
        self.rt_title = None
        self.synopsis = None
        self.error = None


    def get_ratings(self, raise_error=True):
        try:
            self.get_basic_data_from_search()
            self.get_ratings_from_rt_url()
        except Exception as e:
            if raise_error:
                logger.error(f'Raising and failing because raise_error={raise_error}')
                raise e
            else:
                logger.exception(e)
                self.error = str(e)
        return self.format_results()

    def get_basic_data_from_search(self):
        resp = requests.get(self._search_api,
                            params={'q': self.movie_name})
        data = resp.json()
        movies_data = data.get('movies')
        if not movies_data:
            raise RuntimeError(f'RT search returned no movies for {self.movie_name}')

        movie_data = self._select_movie_search_result(movies_data)

        # get the data
        self.rt_title = movie_data['name']
        self.rt_url = f"{self._base_url}{movie_data['url']}"
        self.critics_rating = movie_data.get('meterScore', '')

    def _select_movie_search_result(self, movies):
        for movie in movies:
            year_gap = abs(int(movie['year']) - int(self.year))
            if year_gap <= 1:
                return movie
        else:
            raise RuntimeError(f'no movie found in results ({len(movies)}) '
                               f'within 1 year from {self.year}')

    def get_ratings_from_rt_url(self):
        resp = requests.get(self.rt_url)
        self._scrape_rt_response(resp)

    def _scrape_rt_response(self, resp):
        sel = Selector(text=resp.text)

        self.critics_data = self._get_full_critics_data(resp)
        self.critics_rating = self.critics_data.get(
            'tomatometerAllCritics', {}).get('score', self.critics_rating or '')
        self.critics_avg_score = self.critics_data.get(
            'tomatometerAllCritics', {}).get('averageRating', '')
        self.critics_n_reviews = self.critics_data.get(
            'tomatometerAllCritics', {}).get('ratingCount', '')

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
            'audienceScoreAll', {}).get('ratingCount', '')

        self.rt_title = (self.rt_title or
                         sel.css('.mop-ratings-wrap__title--top::text').extract_first())
        self.rt_title = self.rt_title.strip()

        # synopsis
        self.synopsis = sel.css('#movieSynopsis::text').extract_first() or ''
        self.synopsis = self.synopsis.strip()

    def _get_full_critics_data(self, resp):
        try:
            si_str = 'root.RottenTomatoes.context.scoreInfo'
            return json.loads(re.findall(f'{si_str} = (.*);', resp.text)[0])
        except (json.decoder.JSONDecodeError, TypeError, IndexError):
            logger.error('failed getting structured critics score data')
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

    def format_results(self):
        res = {
            'rt_url': self.rt_url,
            'critics_rating': self.critics_rating,
            'critics_avg_score': self.critics_avg_score,
            'critics_n_reviews': self.critics_n_reviews,
            'audience_rating': self.audience_rating,
            'audience_avg_score': self.audience_avg_score,
            'audience_n_reviews': self.audience_n_reviews,
            'title': self.rt_title,
        }

        if self.error:
            res['error'] = self.error

        return res

