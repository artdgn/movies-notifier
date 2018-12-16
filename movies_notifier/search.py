import re
import urllib

import requests
from parsel import Selector

from movies_notifier.logger import logger

HEADERS = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/33.0.1750.149 Safari/537.36'}


## if blocked should look into https://asciimoo.github.io/searx/index.html


class GoogleFirstPage:

    @classmethod
    def get_results(cls, query):

        results = []

        resp = cls._request(query)

        if not resp.ok:
            logger.error(f'Bad response from search: {resp}')
            raise RuntimeError(f'Bad response from search: {resp}')

        try:
            results = cls._parse_page(resp)

            if len(results) < 5:
                raise RuntimeError('too few results successfully parsed')

        except Exception as e:
            logger.exception(str(e))
            logger.error(f'failed on query: {query}, fix search link scraping')

        if len(results) < 1:
            raise RuntimeError('no results successfully parsed')

        return results

    @classmethod
    def _request(cls, query):
        params = {'q': query}
        return requests.get('https://www.google.com/search', headers=HEADERS, params=params)

    @classmethod
    def _parse_page(cls, resp):
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

    @classmethod
    def im_feeling_lucky(cls, query):
        params = {'q': query, 'btnI': 'I'}
        return requests.get('https://www.google.com/search',
                            headers=HEADERS, params=params)


class DDGFirstPage(GoogleFirstPage):

    @classmethod
    def _request(cls, query):
        params = {'q': query}
        return requests.get('https://www.duckduckgo.com/html/', headers=HEADERS, params=params)

    @classmethod
    def _parse_page(cls, resp):
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

