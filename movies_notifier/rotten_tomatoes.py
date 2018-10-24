import re
import requests

from parsel import Selector

from movies_notifier.logger import logger


def get_first_page_google_results(query):
    results = []
    try:
        resp = requests.get('https://www.google.com/search', params={'q': query})
        sel = Selector(text=resp.text)
        for i in range(1, 10):
            css_text = sel.css('.g:nth-child(1) .r'). \
                css('a::attr(href)').extract_first()
            link = re.findall('(https://\S*)[%|/]', css_text)[0]
            title = sel.css(f'.g:nth-child({i}) .r').css('b::text').extract() \
                    or ''
            title = ' '.join(title)
            results.append({'link': link, 'title': title})
    except Exception as e:
        logger.exception(str(e))
        logger.error(f'failed on query: {query}, got css_text: {css_text}')
    return results


class RTScraper:

    def __init__(self, movie_name, year):
        self.movie_name = movie_name
        self.year = year
        self.rt_url = None

    def get_ratings(self, check_title=True):
        self.get_rt_url_from_google()
        self.get_ratings_from_rt_url()
        return self.format_results(check_title=check_title)

    @staticmethod
    def strip_punctuation(s):
        return re.sub(r'[^\w\s]', '', s)

    def get_rt_url_from_google(self, check_title=True):

        first_page_results = get_first_page_google_results(
            f'movie {self.movie_name} rotten tomatoes {self.year}')

        rt_url = None

        if check_title:
            for r_dict in first_page_results:
                goog_title = self.strip_punctuation(r_dict['title'])
                if \
                        self.strip_punctuation(self.movie_name) in goog_title \
                        and 'Rotten Tomatoes' in goog_title:
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
        if check_title and self.movie_name.lower() not in self.title.lower():
            res['critics_rating'] = None
            res['audience_rating'] = None
            err_msg = f'RT title and input title are different: ' \
                      f'{self.strip_punctuation(self.title)} ' \
                      f'!= {self.strip_punctuation(self.movie_name)}'
            res['error'] = err_msg
            logger.error(err_msg)
        return res

