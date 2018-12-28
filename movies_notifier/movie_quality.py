from movies_notifier.logger import logger


def select_good_movies(movies, critics_threshold=70, audience_threshold=70, mean_threshold=80):
    good_movies = []
    for m in movies:
        rt_data = m['rotten_tomatoes']

        if not rt_data['critics_rating'] or not rt_data['audience_rating']:
            continue

        critics = int(rt_data['critics_rating'])
        audience = int(rt_data['audience_rating'])
        mean = (critics + audience) / 2

        if critics >= critics_threshold and \
                audience >= audience_threshold \
                and mean >= mean_threshold:

            good_movies.append(m)

    logger.info(f'Selected {len(good_movies)} good movies from {len(movies)} movies')
    return good_movies