from argparse import ArgumentParser

from movies_notifier.popcorn import PopcornWithRT
from movies_notifier.movies_store import MoviesStore
from movies_notifier.movie_quality import select_good_movies
from movies_notifier.mailgun import MailgunNotifier


parser = ArgumentParser()
parser.add_argument("-n", "--n-movies", type=int, default=200,
                    help="number of recent movies to check")
parser.add_argument("-s", "--start-offset", type=int, default=1,
                    help="offset from which to start checking")
parser.add_argument("-o", "--overwrite", action="store_true",
                    help="whether to rescrape and overwrite everything (to check if RT scores udpated)")
parser.add_argument("-d", "--delay", type=int, default=5,
                    help="delay between scraping requests")
parser.add_argument("--resend-notifications", action="store_true",
                    help="resend notifications for movies that were already in previous notifications")
args = parser.parse_args()


m_store = MoviesStore()

new_movies = PopcornWithRT.get_new_movies(
    movies_offset_range=(args.start_offset, args.start_offset + args.n_movies),
    skip_func=None if args.overwrite else m_store.exists,
    stop_on_stale_page=True,
    request_delay=args.delay)

m_store.add_movies(
    new_movies, save=True, overwrite=args.overwrite)

good_movies = select_good_movies(m_store.movies.values())

notification_resp = MailgunNotifier.notify(
    good_movies, resend=args.resend_notifications)

