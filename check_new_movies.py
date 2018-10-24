import json

from movies_notifier.mailgun import send_mailgun_notifications
from movies_notifier.popcorn_movies import MoviesStore

m_store = MoviesStore()

new_movies = m_store.get_new_movies()

good_movies = []
for m in new_movies:
    rt_data = m['rotten_tomatoes']
    if rt_data['critics_rating'] and int(rt_data['critics_rating']) > 80 and \
        rt_data['audience_rating'] and int(rt_data['audience_rating']) > 80:
        good_movies.append(m)

if good_movies:
    [m.update({'magnet_1080p': m['torrents'].get('en', {}).get('1080p', {}).get('url')}) for m in good_movies]
    [m.update({'magnet_720p': m['torrents'].get('en', {}).get('720p', {}).get('url')}) for m in good_movies]
    keep_keys = ['_id', 'genres', 'rotten_tomatoes', 'title', 'year', 'magnet_1080p', 'magnet_720p']
    send_movies = [{k:d[k] for k in keep_keys} for d in good_movies]
    resp = send_mailgun_notifications(
        subject=f'{len(send_movies)} new movies',
        text=json.dumps(send_movies, indent=4))