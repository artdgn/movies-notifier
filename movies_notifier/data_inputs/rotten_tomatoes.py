import json
import re
import requests

from parsel import Selector

from movies_notifier.util.logger import logger


class MovieRatingsScraper:

    _base_url = 'https://www.rottentomatoes.com'

    # main site, more results, different ordering, may have noise
    _search_page_url = _base_url + '/search'

    # older, may be deprecated, less results, but returns a JSON
    _direct_search_api_url = _base_url + '/api/private/v2.0/search'

    _audience_api = _base_url + '/napi/audienceScore/'

    _allowed_missing_words = r'the|and'

    class DirectSearchAPIError(Exception):
        pass

    class SearchPageError(Exception):
        pass

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
            self.get_data_from_search()
            self.get_ratings_from_rt_url()
        except Exception as e:
            if raise_error:
                logger.error(f'Raising and failing because raise_error={raise_error}')
                raise e
            else:
                logger.exception(e)
                self.error = str(e)
        return self.format_results()

    def get_data_from_search(self):
        try:
            self.scrape_search_page()
        except self.SearchPageError as e:
            logger.error(f'search page error: {str(e)} for {self.movie_name}, '
                         f'trying direct search instead')
            self.direct_search_api()

    def direct_search_api(self):
        resp = requests.get(self._direct_search_api_url, params={'q': self.movie_name})
        if not resp.ok:
            raise self.DirectSearchAPIError(f'direct search API returned {resp.status_code}')

        data = resp.json()
        movies = data.get('movies', [])

        if not movies:
            raise self.DirectSearchAPIError(f'no movies found in direct search API results '
                                            f'for {self.movie_name}')

        for movie in movies:
            year_gap = abs(int(movie['year']) - int(self.year))
            if year_gap <= 1:
                self.rt_title = movie['name']
                self.rt_url = f"{self._base_url}{movie['url']}"
                self.critics_rating = movie.get('meterScore', '')
                return

        raise self.DirectSearchAPIError(f'no movie within 1 year from {self.year} in '
                                      f'{len(movies)} direct search API results '
                                      f'for {self.movie_name}')

    def scrape_search_page(self):
        resp = requests.get(self._search_page_url, params={'search': self.movie_name})
        if not resp.ok:
            raise self.SearchPageError(f'search page returned {resp.status_code}')

        sel = Selector(text=resp.text)
        js_data = sel.css('#movies-json::text').extract_first()
        data = json.loads(js_data.replace('underfined', 'null'))
        movies = data.get('items', []) if data else []

        if not movies:
            raise self.SearchPageError(f'no movies found in search page results '
                                       f'for {self.movie_name}')

        for movie in movies:
            year_gap = abs(int(movie['releaseYear']) - int(self.year))
            if year_gap <= 1:
                if self._title_match(movie['name']):
                    self.rt_title = movie['name']
                    self.rt_url = movie['url']
                    self.critics_rating = movie.get('tomatometerScore', {}).get('score')
                    self.audience_rating = movie.get('audienceScore', {}).get('score')
                    return
                else:
                    logger.warning(f"skipping insufficient title match: "
                                   f"'{movie['name']}' for '{self.movie_name}'")

        raise self.SearchPageError((f'no movie within 1 year from {self.year} in '
                                    f'{len(movies)} search page results '
                                    f'for {self.movie_name}'))

    @classmethod
    def normalise_title(cls, s):
        s = re.sub(r'[^\w\s]', '', str(s).lower())
        s = re.sub(cls._allowed_missing_words, '', s)
        return ' '.join(s.split())

    def _title_match(self, candidate, min_score = 0.75):
        target = self.normalise_title(self.movie_name)
        candidate = self.normalise_title(candidate)

        target_parts = target.split()
        candidate_parts = candidate.split()

        if not target_parts or not candidate_parts:
            return 0

        score_cand_match = sum([w in target for w in candidate_parts]) / len(candidate_parts)
        score_target_match = sum([w in candidate for w in target_parts]) / len(target_parts)
        return score_cand_match >= min_score or score_target_match >= min_score

    def get_ratings_from_rt_url(self):
        resp = requests.get(self.rt_url)
        self._scrape_rt_response(resp)
        if not self.critics_rating:
            # let's try the direct search because the RT page couldn't be scraped
            # for critics rating
            try:
                self.direct_search_api()
            except self.DirectSearchAPIError as e:
                logger.error(f"failed getting data from direct-search "
                             f"after failing scraping. {e}")

    def _scrape_rt_response(self, resp):
        sel = Selector(text=resp.text)

        self.critics_rating = sel.css('score-board').attrib.get('tomatometerscore', '')
        self.critics_n_reviews = (sel
                                  .css('.scoreboard__link--tomatometer::text')
                                  .extract_first() or '').replace(" Reviews", '')
        ## backup audience data
        # sel.css('score-board').attrib['audiencescore']
        # sel.css('.scoreboard__link--audience::text').extract_first()

        self.critics_rating = sel.css(
            'span[data-qa="tomatometer"]::text').extract_first() or ''
        self.critics_rating = self.critics_rating.strip()[:-1]

        self.audience_data = self._get_full_audience_data(resp)
        self.audience_rating = self.audience_data.get(
            'audienceScoreAll', {}).get('score', '')
        self.audience_avg_score = self.audience_data.get(
            'audienceScoreAll', {}).get('averageRating', '')
        self.audience_n_reviews = self.audience_data.get(
            'audienceScoreAll', {}).get('ratingCount', '')

        self.rt_title = (self.rt_title or
                         sel
                         .css('.scoreboard__title::text')
                         .extract_first() or
                         '').strip()

        # synopsis
        self.synopsis = sel.css('#movieSynopsis::text').extract_first() or ''
        self.synopsis = self.synopsis.strip()

    def _get_full_audience_data(self, resp):
        try:
            fd_str = 'root.RottenTomatoes.context.fandangoData'
            js_data = re.findall(f'{fd_str} = (.*);', resp.text)[0]
            ems_id = re.findall(r'emsId":"(.*?)"', js_data)[0]
            resp_aud = requests.get(self._audience_api + ems_id)
            return resp_aud.json()
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
