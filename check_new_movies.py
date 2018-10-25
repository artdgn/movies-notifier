import json

from movies_notifier.mailgun import send_mailgun_notifications
from movies_notifier.movies import MoviesStore

m_store = MoviesStore()

new_movies = m_store.get_new_movies()
good_movies = m_store.select_good_movies(new_movies)

if good_movies:
    m_df = m_store.movie_list_to_export_df(good_movies)

    # # html attachment
    # movies_html = m_store.movie_df_to_html_table(m_df)
    # html_file = './data/html_table_file.html'
    # open(html_file, 'wt').write(movies_html)
    #
    # # csv attachment
    # csv_file = './data/table.csv'
    # m_df.to_csv(csv_file, index=None)

    resp = send_mailgun_notifications(
        subject=f'{len(good_movies)} new movies from popcorn',
        text=json.dumps(m_store.remove_fields(good_movies), indent=4),
        # html=movies_html
        # files=[html_file]
        # files=[csv_file]
    )


