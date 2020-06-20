import functools
import sys
from argparse import ArgumentParser

from movies_notifier import movie_quality
from movies_notifier.data_inputs.popcorn import PopcornWithRT
from movies_notifier.persistance.movies import MoviesStore
from movies_notifier.persistance.notifications import Notifier


def parse_args():
    if len(sys.argv) == 1:
        sys.argv.append("-h")  # print help if no args

    parser = ArgumentParser()

    parser.add_argument("-n", "--n-movies", type=int, required=True,
                        help="number of recent movies to scan")

    parser.add_argument("-f", "--first-offset", type=int, default=0,
                        help="offset from which to start checking (default 0)")

    parser.add_argument("-s", "--sort", type=str, default="all",
                        help="type of sort for popcorn-api. default 'all' "
                             "(all possible sorts will be checked). "
                             "other options: 'l' (last added), 't' (trending), 'p' (popularity) "
                             "or any mix of those.")
    parser.add_argument("-ss", "--stop-on-stale", action="store_true",
                        help="stop scanning popcorn results if one full page is stale")
    parser.add_argument("-o", "--overwrite", action="store_true",
                        help="whether to rescrape and overwrite files with no RT data")

    parser.add_argument("-se", "--search-engine", type=str, default="g",
                        help="which search engine to use to find the RT page."
                             "d: duck-duck-go, g: google. ")

    parser.add_argument("-c", "--cookies-source", type=str, default="none",
                        help="which browser's cookies to use [none, firefox, chrome]")

    parser.add_argument("-e", "--email", action="store_true",
                        help="notify by email (use if you have email notifier set up)")

    parser.add_argument("-g", "--gspread-share", type=str,
                        help="email address for uploading and sharing the google-sheet (don't specify "
                             "if google-docs API is not set up)")

    return parser.parse_args()


def main():
    args = parse_args()

    m_store = MoviesStore()

    movies_checker = PopcornWithRT(
        search_engine=args.search_engine,
        cookies=args.cookies_source)

    movies_checker.get_new_movies(
        movies_offset_range=(args.first_offset,
                             args.first_offset + args.n_movies),
        skip_func=m_store.has_rt_data if args.overwrite else m_store.exists,
        sort=args.sort,
        stop_on_stale_page=args.stop_on_stale,
        save_func=functools.partial(m_store.add_movie,
                                    save=True,
                                    overwrite=args.overwrite)
    )

    # select good movies
    good_movies = movie_quality.select_good_movies(m_store.movies.values())

    # notify
    notified_movies = \
        Notifier(send_mailgun_email=args.email,
                 gdocs_share_email=args.gspread_share). \
            notify(good_movies)

    # html table
    if notified_movies:
        m_store.write_html_table_for_list(notified_movies)
