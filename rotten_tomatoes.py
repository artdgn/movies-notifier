import re
import requests

from parsel import Selector

from logger import logger


def get_first_google_result(query):
    try:
        resp = requests.get('https://www.google.com/search', params={'q': query})
        sel = Selector(text=resp.text)
        css_text = sel.css('.g:nth-child(1) .r'). \
            css('a::attr(href)').extract_first()
        return re.findall('(https://\S*)[%|/]', css_text)[0]
    except Exception as e:
        logger.exception(str(e))
        logger.error(f'failed on query: {query}, got css_text: {css_text}')


class RTScraper:

    def __init__(self, movie_name, year):
        self.movie_name = movie_name
        self.year = year
        self.rt_url = None

    def get_ratings(self, check_title=True):
        self.get_rt_url_from_google()
        self.get_ratings_from_rt_url()
        return self.format_results(check_title=check_title)

    def get_rt_url_from_google(self):
        self.rt_url = get_first_google_result(f'movie {self.movie_name} rotten tomatoes {self.year}')

    def get_ratings_from_rt_url(self):
        resp = requests.get(self.rt_url)
        sel = Selector(text=resp.text)
        self.critics_rating = sel.css('#tomato_meter_link '
                               '.superPageFontColor span::text').extract_first()
        audience_text = sel.css('.meter-value '
                                '.superPageFontColor::text').extract_first()
        self.audience_rating = audience_text[:-1] if audience_text is not None else audience_text
        self.title = sel.css('#movie-title::text').extract_first().strip()
        self.synopsis = sel.css('#movieSynopsis::text').extract_first().strip()

    def format_results(self, check_title=True):
        res = {
            'rt_url': self.rt_url,
            'critics_rating': self.critics_rating,
            'audience_rating': self.audience_rating,
            'title': self.title,
            'synopsis': self.synopsis
        }
        if check_title and self.movie_name.lower() !=  self.title:
            res['critics_rating'] = None
            res['audience_rating'] = None
            res['error'] = 'RT title and input title are different'
        return res

