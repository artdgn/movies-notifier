import re

import requests
from parsel import Selector

from movies_notifier.logger import logger


def get_first_page_google_results(query):
    results = []
    try:
        resp = requests.get('https://www.google.com/search', params={'q': query})
        sel = Selector(text=resp.text)
        for i in range(1, 11):
            css_text = sel.css('.g:nth-child(1) .r'). \
                css('a::attr(href)').extract_first()
            link = re.findall('(https://\S*)[%|/]', css_text)[0]
            title = sel.css(f'.g:nth-child({i}) .r').css('b::text').extract() \
                    or ''
            title = ' '.join(title)
            results.append({'link': link, 'title': title})
    except Exception as e:
        logger.exception(str(e))
        logger.error(f'failed on query: {query}, got css_text: {css_text}, '
                     f'fix google link scraping')
    return results