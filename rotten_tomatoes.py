import re
import requests

from parsel import Selector


def get_first_google_result(query):
    resp = requests.get('https://www.google.com/search', params={'q': query})
    sel = Selector(text=resp.text)
    css_text = sel.css('.g:nth-child(1) .r'). \
        css('a::attr(href)').extract_first()
    return re.findall('(https://\S*)/&', css_text)[0]


class RTScraper:

    def __init__(self, movie_name):
        self.movie_name = movie_name
        self.rt_url = None

    def get_ratings(self):
        self.get_rt_url_from_google()
        self.get_ratings_from_rt_url()
        return self.format_results()

    def get_rt_url_from_google(self):
        self.rt_url = get_first_google_result(f'movie {self.movie_name} rotten tomatoes')

    def get_ratings_from_rt_url(self):
        resp = requests.get(self.rt_url)
        sel = Selector(text=resp.text)
        self.critics_rating = sel.css('#tomato_meter_link '
                               '.superPageFontColor span::text').extract_first()
        audience_text = sel.css('.meter-value '
                                '.superPageFontColor::text').extract_first()
        self.audience_rating = audience_text[:-1] if audience_text is not None else audience_text

    def format_results(self):
        return {
            'rt_url': self.rt_url,
            'critics_rating': self.critics_rating,
            'audience_rating': self.audience_rating
        }
