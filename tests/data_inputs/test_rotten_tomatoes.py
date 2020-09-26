import random
import time

import pytest

from movies_notifier.data_inputs import rotten_tomatoes


@pytest.mark.integration
class TestRT:
    test_delay_sec = 2
    rt_cls = rotten_tomatoes.MovieRatingsScraper

    @pytest.fixture(autouse=True)
    def delay(self):
        """
        Always add delay before evert test
        """
        time.sleep(self.test_delay_sec + random.random())

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

    def test_direct_search_api_simple(self):
        name = 'Thank You for Smoking'
        sut = self.rt_cls(name, 2006)
        sut.direct_search_api()
        assert sut.rt_url == 'https://www.rottentomatoes.com/m/thank_you_for_smoking'
        assert sut.rt_title == name
        assert sut.critics_rating

    @pytest.mark.parametrize('name, year, expected_url, expect_rating', [
        ('red',
         2010,
         'https://rottentomatoes.com/m/red',
         True),
        ("Edgar Allen Poe's Ligeia",
         2009,
         'https://rottentomatoes.com/m/edgar_allan_poes_mystery_theatre',
         False),
    ])
    def test_scrape_search_page_simple(self, name, year, expected_url, expect_rating):
        sut = self.rt_cls(name, year)
        sut.scrape_search_page()
        assert sut.rt_url == expected_url
        if expect_rating:
            assert sut.critics_rating

    def test_get_ratings(self):
        name = 'Thank You for Smoking'
        sut = self.rt_cls(name, 2006)
        res = sut.get_ratings()

        assert res['rt_url'] == 'https://rottentomatoes.com/m/thank_you_for_smoking'
        assert res['title'] == name
        assert res['critics_rating']
        assert res['critics_avg_score']
        assert res['critics_n_reviews']
        assert res['audience_rating']
        assert res['audience_avg_score']
        assert res['audience_n_reviews']

    def test_get_ratings_errors(self):
        name = 'nosuchmovie'
        sut = self.rt_cls(name, 2000)
        res = sut.get_ratings(raise_error=False)
        assert 'no movies' in res['error']

        with pytest.raises(sut.DirectSearchAPIError):
            sut.get_ratings(raise_error=True)
