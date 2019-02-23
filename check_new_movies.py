import functools
from argparse import ArgumentParser

from movies_notifier.popcorn import PopcornWithRT
from movies_notifier.movies_store import MoviesStore
from movies_notifier.movie_quality import select_good_movies
from movies_notifier.mailgun import Notifier


parser = ArgumentParser()
parser.add_argument("-ne", "--no-email", action="store_true",
                    help="don't notify by email (use this if you don't have email notifier set up)")
parser.add_argument("-n", "--n-movies", type=int, default=200,
                    help="number of recent movies to check (default 200)")
parser.add_argument("-f", "--first-offset", type=int, default=1,
                    help="offset from which to start checking (default 1)")
parser.add_argument("-s", "--sort", type=str, default="ltp",
                    help="type of sort for popcorn-api. default 'ltp' "
                         "(last added + trending + popularity: all three will be checked). "
                         "other options: 'l' (last added), 't' (trending), 'p' (popularity) "
                         "or any mix of those.")
parser.add_argument("-e", "--search-engine", type=str, default="g-cookies",
                    help="which search engine to use to find the RT page and whether to use browser cookies."
                         "d: duck-duck-go, g: google. g-cookies: google chrome with your cookies.. ")
parser.add_argument("-o", "--overwrite", action="store_true",
                    help="whether to rescrape and overwrite files with no RT data")
parser.add_argument("-d", "--delay-range", type=str, default='61-120',
                    help="delay in seconds between scraping requests (default 61-120)")
parser.add_argument("--resend-notifications", action="store_true",
                    help="resend notifications for movies that were already in previous notifications")
args = parser.parse_args()


m_store = MoviesStore()

# get new movies
new_movies = PopcornWithRT(
    request_delay_range=args.delay_range,
    search_engine=args.search_engine,
    stop_on_errors=True).\
    get_new_movies(
        movies_offset_range=(args.first_offset, args.first_offset + args.n_movies),
        skip_func=m_store.has_full_rt_data if args.overwrite else m_store.exists,
        sort=args.sort,
        stop_on_stale_page=True,
        save_func=functools.partial(m_store.add_movie, save=True, overwrite=args.overwrite)
        )

# select good movies
good_movies = select_good_movies(m_store.movies.values())

# notify
notification_backend = 'none' if args.no_email else 'mailgun'
notified_movies = \
    Notifier(backend=notification_backend).\
    notify(good_movies, resend=args.resend_notifications)

# html table
if notified_movies:
    m_store.write_html_table_for_list(notified_movies)