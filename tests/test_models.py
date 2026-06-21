from streaming_availability.models import (
    ChangesResult,
    Country,
    Genre,
    SearchResult,
    Show,
)

from .fixtures import (
    SAMPLE_CHANGES_RESULT,
    SAMPLE_COUNTRY,
    SAMPLE_SEARCH_RESULT,
    SAMPLE_SHOW,
)


def test_show_basic_fields():
    show = Show(SAMPLE_SHOW)
    assert show.id == "tt0111161"
    assert show.title == "The Shawshank Redemption"
    assert show.show_type == "movie"
    assert show.is_movie is True
    assert show.is_series is False
    assert show.release_year == 1994
    assert show.rating == 91


def test_show_genres():
    show = Show(SAMPLE_SHOW)
    genres = show.genres
    assert len(genres) == 1
    assert isinstance(genres[0], Genre)
    assert genres[0].id == "drama"
    assert genres[0].name == "Drama"


def test_show_streaming_options():
    show = Show(SAMPLE_SHOW)
    options = show.streaming_options
    assert "us" in options
    us_options = options["us"]
    assert len(us_options) == 1
    option = us_options[0]
    assert option.service.id == "netflix"
    assert option.type == "subscription"
    assert option.link == "https://netflix.com/watch/123"
    assert option.expires_soon is False
    assert option.available_since == 1600000000
    assert len(option.audios) == 1
    assert option.audios[0].language == "en"
    assert len(option.subtitles) == 1
    assert option.subtitles[0].closed_captions is True


def test_show_to_dict_roundtrip():
    show = Show(SAMPLE_SHOW)
    assert show.to_dict() == SAMPLE_SHOW


def test_show_repr_and_eq():
    show1 = Show(SAMPLE_SHOW)
    show2 = Show(dict(SAMPLE_SHOW))
    assert show1 == show2
    assert "Show(" in repr(show1)


def test_search_result():
    result = SearchResult(SAMPLE_SEARCH_RESULT)
    assert result.has_more is True
    assert result.next_cursor == "abc123"
    assert len(result.shows) == 1
    assert isinstance(result.shows[0], Show)
    assert result.shows[0].title == "The Shawshank Redemption"


def test_country():
    country = Country(SAMPLE_COUNTRY)
    assert country.country_code == "us"
    assert country.name == "United States"
    services = country.services
    assert len(services) == 1
    assert services[0].id == "netflix"
    assert services[0].streaming_option_types["subscription"] is True


def test_changes_result():
    result = ChangesResult(SAMPLE_CHANGES_RESULT)
    assert result.has_more is False
    assert len(result.changes) == 1
    change = result.changes[0]
    assert change.change_type == "new"
    assert change.item_type == "show"
    assert change.show_id == "tt0111161"
    assert "tt0111161" in result.shows
    assert isinstance(result.shows["tt0111161"], Show)
