import json

from movies_notifier.mailgun import send_mailgun_notifications
from movies_notifier.movies import MoviesStore

m_store = MoviesStore()

new_movies = m_store.get_new_movies()
good_movies = m_store.select_good_movies(new_movies)

if good_movies:
    resp = send_mailgun_notifications(
        subject=f'{len(good_movies)} new movies from popcorn',
        text=json.dumps(m_store.remove_fields(good_movies), indent=4))