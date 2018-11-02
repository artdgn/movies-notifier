from movies_notifier.logger import logger


def select_good_movies(new_movies, critics_threshold=80, audience_threshold=80):
    good_movies = []
    for m in new_movies:
        rt_data = m['rotten_tomatoes']
        if \
                rt_data['critics_rating'] and \
                int(rt_data['critics_rating']) > critics_threshold and \
                rt_data['audience_rating'] and \
                int(rt_data['audience_rating']) > audience_threshold:
            good_movies.append(m)
    logger.info(f'Selected {len(good_movies)} good movies from {len(new_movies)} new movies')
    return good_movies