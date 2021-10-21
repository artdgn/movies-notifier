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
        assert sut.critics_n_reviews
        assert sut.audience_rating
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
         'https://www.rottentomatoes.com/m/red',
         True),
        ("Edgar Allen Poe's Ligeia",
         2009,
         'https://www.rottentomatoes.com/m/edgar_allan_poes_mystery_theatre',
         False),
    ])
    def test_scrape_search_page_simple(self, name, year, expected_url, expect_rating):
        sut = self.rt_cls(name, year)
        sut.scrape_search_page()
        assert sut.rt_url == expected_url
        if expect_rating:
            assert sut.critics_rating

    def test_get_ratings_simple(self):
        name = 'Thank You for Smoking'
        sut = self.rt_cls(name, 2006)
        res = sut.get_ratings()

        assert res['rt_url'] == 'https://www.rottentomatoes.com/m/thank_you_for_smoking'
        assert res['title'] == name
        assert res['critics_rating']
        assert res['critics_n_reviews']
        assert res['audience_rating']
        assert res['audience_n_reviews']

    def test_get_ratings_errors(self):
        name = 'nosuchmovie'
        sut = self.rt_cls(name, 2000)
        res = sut.get_ratings(raise_error=False)
        assert 'no movies' in res['error']

        with pytest.raises(sut.DirectSearchAPIError):
            sut.get_ratings(raise_error=True)

    def test_get_ratings_non_json_javascript_data(self):
        name = 'The Many Lives of Nick Buoniconti'
        sut = self.rt_cls(name, 2019)
        res = sut.get_ratings()
        assert 'error' not in res

    def test_get_ratings_insufficient_title_match(self):
        # search-page has bad results, exact match in direct search
        sut = self.rt_cls('One Glorious Sunset', 2020)
        _ = sut.get_ratings()
        assert sut.rt_title == sut.movie_name

        # not found
        with pytest.raises(sut.DirectSearchAPIError):
            # also "Camp Blood 8: Revelations"
            self.rt_cls('Hooligan Escape The Russian Job', 2018).get_ratings()

        # insufficient matches
        with pytest.raises(sut.DirectSearchAPIError):
            self.rt_cls('Portrait of Animal Behavior', 2020).get_ratings()


