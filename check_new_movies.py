from movies_notifier.popcorn import PopcornWithRT
from movies_notifier.movies_store import MoviesStore
from movies_notifier.movie_quality import select_good_movies
from movies_notifier.mailgun import MailgunNotifier


m_store = MoviesStore()

new_movies = PopcornWithRT.get_new_movies(
    movies_offset_range=(1, 200),
    skip_func=m_store.exists,
    stop_on_stale_page=True,
    request_delay=5)

m_store.add_movies(new_movies)

good_movies = select_good_movies(m_store.movies.values())

notification_resp = MailgunNotifier.notify(good_movies)

