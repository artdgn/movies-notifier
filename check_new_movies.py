from popcorn_movies import MoviesStore, PopcornClient

pop = PopcornClient()

m_store = MoviesStore()

page_2_movies = pop.get_popcorn_movies(2)
m_store.save_movies(page_2_movies)

new_movies = m_store.get_new_movies()
