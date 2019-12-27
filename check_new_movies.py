import functools
from argparse import ArgumentParser

from movies_notifier.movie_quality import select_good_movies
from movies_notifier.movies_store import MoviesStore
from movies_notifier.notification import Notifier
from movies_notifier.popcorn import PopcornWithRT


def parse_args():
    parser = ArgumentParser()

    parser.add_argument("-n", "--n-movies", type=int, default=200,
                        help="number of recent movies to check (default 200)")
    parser.add_argument("-f", "--first-offset", type=int, default=1,
                        help="offset from which to start checking (default 1)")
    parser.add_argument("-s", "--sort", type=str, default="all",
                        help="type of sort for popcorn-api. default 'all' "
                             "(all possible sorts will be checked). "
                             "other options: 'l' (last added), 't' (trending), 'p' (popularity) "
                             "or any mix of those.")
    parser.add_argument("-sp", "--stop-on-stale-page", action="store_false",
                        help="stop scanning popcorn results if one full page is stale")
    parser.add_argument("-o", "--overwrite", action="store_true",
                        help="whether to rescrape and overwrite files with no RT data")

    parser.add_argument("-e", "--search-engine", type=str, default="g",
                        help="which search engine to use to find the RT page."
                             "d: duck-duck-go, g: google. ")
    parser.add_argument("-c", "--cookies-source", type=str, default="firefox",
                        help="which browser's cookies to use [none, firefox, chrome]")

    parser.add_argument("-d", "--delay-range", type=str, default='61-120',
                        help="delay in seconds between scraping requests (default 61-120)")
    parser.add_argument("-nf", "--number-consequtive-fails", type=int, default=5,
                        help="number of consequtive scrape errors after which to stop (default 3)")

    parser.add_argument("-ne", "--no-email", action="store_true",
                        help="don't notify by email (set to false if you don't have email notifier set up)")
    parser.add_argument("-gs", "--gspread-share", type=str,
                        help="email address for uploading and sharing the google-sheet (don't specify "
                             "if google-docs API is not set up)")
    parser.add_argument("--resend-notifications", action="store_true",
                        help="resend notifications for movies that were already in previous notifications")

    return parser.parse_args()


def main():
    args = parse_args()

    m_store = MoviesStore()

    movies_checker = PopcornWithRT(
        request_delay_range=args.delay_range,
        search_engine=args.search_engine,
        cookies=args.cookies_source,
        number_fails_threshold=args.number_consequtive_fails)

    new_movies = movies_checker.get_new_movies(
        movies_offset_range=(args.first_offset,
                             args.first_offset + args.n_movies),
        skip_func=m_store.has_rt_data if args.overwrite else m_store.exists,
        sort=args.sort,
        stop_on_stale_page=args.stop_on_stale_page,
        save_func=functools.partial(m_store.add_movie,
                                    save=True,
                                    overwrite=args.overwrite)
    )

    # select good movies
    good_movies = select_good_movies(m_store.movies.values())

    # notify
    notified_movies = \
        Notifier(send_mailgun_email=not args.no_email,
                 gdocs_share_email=args.gspread_share). \
            notify(good_movies, resend=args.resend_notifications)

    # html table
    if notified_movies:
        m_store.write_html_table_for_list(notified_movies)


if __name__ == '__main__':
    main()
