import json

from movies_notifier.mailgun import send_mailgun_notifications
from movies_notifier.movies import MoviesStore

import requests_cache

requests_cache.install_cache(expire_after=2*86400)

m_store = MoviesStore()

new_movies = m_store.get_new_movies()
good_movies = m_store.select_good_movies(new_movies)

if good_movies:
    send_movies = m_store.remove_fields(good_movies)
    resp = send_mailgun_notifications(
        subject=f'{len(send_movies)} new movies from popcorn',
        text=json.dumps(send_movies, indent=4))