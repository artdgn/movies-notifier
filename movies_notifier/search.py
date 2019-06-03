import re
import urllib

import requests
from parsel import Selector
from browsercookie import chrome as chrome_cookies

from movies_notifier.logger import logger


HEADERS = {
    'authority': 'www.google.com',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image'
              '/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,'
                  ' like Gecko) Chrome/74.0.3729.157 Safari/537.36',
}


class Scraper:

    def __init__(self, search_setting):
        self.cookiejar = None
        self._engine = None
        if 'cookies' in search_setting:
            self.cookiejar = chrome_cookies()

        if search_setting.startswith('d'):
            self._engine = DuckDuckGo()
        elif search_setting.startswith('g'):
            self._engine = Google()
        else:
            raise ValueError(f'Unknown search-engine option: {search_setting}')

    def get_results(self, query):

        results = []

        resp = self._engine.request(query, cookies=self.cookiejar)

        if not resp.ok:
            logger.error(f'Bad response from search: {resp}')
            raise RuntimeError(f'Bad response from search: {resp}')

        try:
            results = self._engine.parse_page(resp)

            if len(results) < 5:
                raise RuntimeError(f'too few results successfully parsed: {query}')

        except Exception as e:
            logger.exception(str(e))
            logger.error(f'failed on query: {query}, fix search link scraping')

        if len(results) < 1:
            raise RuntimeError('no results successfully parsed')

        return results


class Google:

    @staticmethod
    def request(query, cookies=None):
        params = {'q': query}
        return requests.get('https://www.google.com/search',
                            headers=HEADERS, params=params, cookies=cookies)

    @staticmethod
    def parse_page(resp):
        results = []
        sel = Selector(text=resp.text)
        for i in range(1, 11):
            css_text = sel.css(f'.g:nth-child({i}) .r'). \
                css('a::attr(href)').extract_first()
            if not css_text: continue

            link_part = re.findall('(http[s]{0,1}://\S*)', css_text)
            if not link_part: continue

            link = link_part[0].split('&')[0]
            title = sel.css(f'.g:nth-child({i}) .r').css('::text').extract() \
                    or ''
            title = ' '.join(title)
            results.append({'link': link, 'title': title})
        return results

    @staticmethod
    def im_feeling_lucky(query, cookies=None):
        params = {'q': query, 'btnI': 'I'}
        return requests.get('https://www.google.com/search',
                            headers=HEADERS, params=params, cookies=cookies)


class DuckDuckGo:

    @staticmethod
    def request(query, cookies=None):
        params = {'q': query}
        return requests.get('https://www.duckduckgo.com/html/',
                            headers=HEADERS, params=params, cookies=cookies)

    @staticmethod
    def parse_page(resp):
        results = []
        sel = Selector(text=resp.text)
        for i in range(1, 11):
            link_sel = sel.css(f'.web-result:nth-child({i}) .result__a')

            if not link_sel: continue

            link_part_css = link_sel.css('::attr(href)').extract_first()
            link_part_decoded = urllib.parse.unquote(link_part_css)

            link_match = re.findall('(http[s]{0,1}://\S*)', link_part_decoded)

            if not link_match: continue

            link = link_match[0]

            title_a = link_sel.css('a::text').extract()
            title_b = link_sel.css('b::text').extract()
            title = ' '.join(title_a + title_b)

            results.append({'link': link, 'title': title})
        return results
