import pandas as pd

from movies_notifier import pandas_utils
from movies_notifier.movies_store import MoviesStore

pandas_utils.console_settings()

m_store = MoviesStore()

df = m_store.movies_df()

# cut off analysis
df['critics_rating'] = pd.to_numeric(df['critics_rating'])
df['audience_rating'] = pd.to_numeric(df['audience_rating'])
df['year'] = pd.to_numeric(df['year'])

df_num = df[~df['critics_rating'].isnull() & ~df['audience_rating'].isnull()].copy()
df_num.drop(['magnet_720p', 'error', 'scrape_date'], axis=1, inplace=True)

filt = (df_num['critics_rating'] >= 80) & (df_num['audience_rating'] >= 80 ) & (df_num['year'] >= 2017 )
df_out = df_num[filt].sort_values(['critics_rating', 'audience_rating'], ascending=False)

filename = 'data/html_table_file.html'
open(filename, 'wt').write(m_store.movie_df_to_html_table(df_out))