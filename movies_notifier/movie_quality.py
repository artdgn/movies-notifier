import typing
from movies_notifier.logger import logger
from movies_notifier.movies_store import Movie


def select_good_movies(movies: typing.List[Movie],
                       critics_threshold=70,
                       audience_threshold=70,
                       mean_threshold=80,
                       one_none_threshold=95):
    good_movies = []
    for m in movies:
        critics = int(m.rt_critics()) if m.rt_critics() else None
        audience = int(m.rt_audience()) if m.rt_audience() else None

        if critics and critics < critics_threshold:
            continue

        if audience and audience < audience_threshold:
            continue

        ratings = [r for r in [critics, audience] if isinstance(r, int)]
        if ratings and (sum(ratings) / 2 >= mean_threshold or
                        min(ratings) >= one_none_threshold):
            good_movies.append(m)

    logger.info(f'Selected {len(good_movies)} good movies from {len(movies)} movies')
    return good_movies