import pytest

from movies_notifier.data_inputs import rotten_tomatoes


@pytest.mark.integration
class TestRT:
    rt_cls = rotten_tomatoes.MovieRatingsScraper

    def test_get_ratings_from_rt_url_simple(self):
        sut = self.rt_cls('Thank You for Smoking', 2006)
        sut.rt_url = 'https://www.rottentomatoes.com/m/thank_you_for_smoking'
        sut.get_ratings_from_rt_url()

        assert sut.critics_rating
        assert sut.critics_avg_score
        assert sut.critics_n_reviews
        assert sut.audience_rating
        assert sut.audience_avg_score
        assert sut.audience_n_reviews
        assert sut.rt_title
        assert sut.synopsis

    def test_get_basic_data_from_search_simple(self):
        name = 'Thank You for Smoking'
        sut = self.rt_cls(name, 2006)
        sut.get_basic_data_from_search()
        assert sut.rt_url == 'https://www.rottentomatoes.com/m/thank_you_for_smoking'
        assert sut.rt_title == name
        assert sut.critics_rating
