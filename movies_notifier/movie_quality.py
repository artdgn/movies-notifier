import typing
from movies_notifier.util.logger import logger
from movies_notifier.persistance.movies import Movie


def select_good_movies(movies: typing.List[Movie],
                       critics_threshold=70,
                       audience_threshold=70,
                       mean_threshold=80,
                       one_none_threshold=95,
                       critics_n_reviews_threshold=1,
                       audience_n_reviews_threshold=10,
                       ):
    good_movies = []
    for m in movies:
        critics, audience = None, None

        if m.rt_critics_rating(critics_n_reviews_threshold):
            critics = int(m.rt_critics_rating())

        if m.rt_audience_rating(audience_n_reviews_threshold):
            audience = int(m.rt_audience_rating())

        if critics and critics < critics_threshold:
            continue

        if audience and audience < audience_threshold:
            continue

        ratings = [r for r in [critics, audience] if isinstance(r, int)]
        if ratings and (sum(ratings) / 2 >= mean_threshold or
                        min(ratings) >= one_none_threshold):
            good_movies.append(m)

    logger.info(f'Selected {len(good_movies)} '
                f'good movies from {len(movies)} movies')
    return good_movies
