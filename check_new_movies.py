import json

from movies_notifier.mailgun import send_mailgun_notifications
from movies_notifier.movie_quality import select_good_movies
from movies_notifier.popcorn import PopcornWithRT
from movies_notifier.movies_store import MoviesStore


m_store = MoviesStore()

new_movies = PopcornWithRT.get_new_movies(
    max_pages=3, skip_func=m_store.exists,
    stop_on_stale_page=True, request_delay=5)

m_store.save_movies(new_movies)

good_movies = select_good_movies(new_movies)

if good_movies:
    resp = send_mailgun_notifications(
        subject=f'{len(good_movies)} new movies from popcorn',
        text=json.dumps(m_store.remove_fields(good_movies), indent=4)
    )


