import json

import pandas as pd

from movies_notifier import pandas_utils
from movies_notifier.movies_store import MoviesStore

pandas_utils.console_settings()

m_store = MoviesStore()

df = m_store.movies_df()

# cut off analysis
df['critics_rating'] = pd.to_numeric(df['critics_rating'])
df['audience_rating'] = pd.to_numeric(df['audience_rating'])

df_num = df[~df['critics_rating'].isnull() & ~df['audience_rating'].isnull()].copy()
df_num.drop(['magnet_1080p', 'magnet_720p'], axis=1, inplace=True)

df_num.plot.scatter(x='critics_rating', y='audience_rating')

# filt = (df_num['critics_rating'] > 90) & (df_num['audience_rating'] < 80 )
# filt = (df_num['critics_rating'] < 80) & (df_num['audience_rating'] > 98 )
# filt = (df_num['critics_rating'] > 98) & (df_num['audience_rating'] < 80 )
filt = (df_num['critics_rating'] >= 90) & (df_num['audience_rating'] >= 90 )
print(df_num[filt].sort_values('audience_rating'))