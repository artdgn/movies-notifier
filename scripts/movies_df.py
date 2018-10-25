import json

import pandas as pd

from movies_notifier import pandas_utils
from movies_notifier.movies import MoviesStore

pandas_utils.console_settings()

m_store = MoviesStore()
m_store.load_movies()

movie_list = list(m_store.movies.values())

df = m_store.movie_list_to_export_df(movie_list)

# cut off analysis
df['critics_rating'] = pd.to_numeric(df['critics_rating'])
df['audience_rating'] = pd.to_numeric(df['audience_rating'])

df_num = df[~df['critics_rating'].isnull() & ~df['audience_rating'].isnull()].copy()
df_num.drop(['magnet_1080p', 'magnet_720p'], axis=1, inplace=True)

df_num.plot.scatter(x='critics_rating', y='audience_rating')

df_num[(df_num['critics_rating'] > 90) & (df_num['audience_rating'] < 80 )].sort_values('audience_rating')