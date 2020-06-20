import pandas as pd

from movies_notifier import movie_quality
from movies_notifier.persistance.movies import MoviesStore
from movies_notifier.util import pandas_utils

pandas_utils.console_settings()

m_store = MoviesStore()

# only selected
df = m_store.movie_list_to_export_df(
    movie_quality.select_good_movies(m_store.movies.values()))

df['critics_rating'] = pd.to_numeric(df['critics_rating'])
df['audience_rating'] = pd.to_numeric(df['audience_rating'])
df.insert(2, 'mean_rating', df[['audience_rating', 'critics_rating']].mean(1))
df.insert(0, 'year', df.pop('year'))

df_out = (df[~df['critics_rating'].isnull() & ~df['audience_rating'].isnull()].copy()
          .drop(['magnet_720p', 'scrape_date',
                 'critics_avg_score', 'critics_n_reviews',
                 'audience_avg_score', 'audience_n_reviews'], axis=1)
          .dropna(subset=['magnet_1080p'])
          .sort_values(['year', 'mean_rating'], ascending=False))

filename = 'data/html_table_file.html'
open(filename, 'wt').write(
    df_out.style
        .hide_index()
        .format('<b>{}</b>', subset='title')
        .format('<b>{}</b>', subset='year')
        .format('<a target="_blank" href={}>rotten tomatoes</a>', subset='rt_url')
        .format('<a href={}>magnet</a>', subset='magnet_1080p')
        .format('<b>{:.1f}</b>', subset=['mean_rating', 'critics_rating', 'audience_rating'])
        .bar(color='#84f282', vmin=80, vmax=100,
             subset=['mean_rating', 'critics_rating', 'audience_rating'])
        .render())
