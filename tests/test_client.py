import responses
import pytest

from streaming_availability import (
    NotFoundError,
    RateLimitError,
    StreamingAvailabilityClient,
)
from streaming_availability._base import DEFAULT_BASE_URL, RAPIDAPI_BASE_URL

from .fixtures import (
    ERROR_NOT_FOUND,
    SAMPLE_CHANGES_RESULT,
    SAMPLE_COUNTRIES,
    SAMPLE_COUNTRY,
    SAMPLE_GENRES,
    SAMPLE_SEARCH_RESULT,
    SAMPLE_SHOW,
)


@pytest.fixture
def client():
    with StreamingAvailabilityClient(api_key="test-key") as c:
        yield c


def test_requires_api_key():
    with pytest.raises(ValueError):
        StreamingAvailabilityClient(api_key="")


def test_default_base_url():
    client = StreamingAvailabilityClient(api_key="key")
    assert client.base_url == DEFAULT_BASE_URL


def test_rapidapi_base_url():
    client = StreamingAvailabilityClient(api_key="key", use_rapidapi=True)
    assert client.base_url == RAPIDAPI_BASE_URL


@responses.activate
def test_get_show_sends_correct_request_and_headers(client):
    responses.add(
        responses.GET,
        f"{DEFAULT_BASE_URL}/shows/tt0111161",
        json=SAMPLE_SHOW,
        status=200,
    )
    show = client.get_show("tt0111161", country="us", series_granularity="show")

    assert show.title == "The Shawshank Redemption"
    sent = responses.calls[0].request
    assert sent.headers["X-API-Key"] == "test-key"
    assert "country=us" in sent.url
    assert "series_granularity=show" in sent.url


@responses.activate
def test_rapidapi_header_used_when_configured():
    client = StreamingAvailabilityClient(api_key="rapid-key", use_rapidapi=True)
    responses.add(
        responses.GET,
        f"{RAPIDAPI_BASE_URL}/shows/tt0111161",
        json=SAMPLE_SHOW,
        status=200,
    )
    client.get_show("tt0111161")
    sent = responses.calls[0].request
    assert sent.headers["X-RapidAPI-Key"] == "rapid-key"
    assert "X-API-Key" not in sent.headers


@responses.activate
def test_get_countries(client):
    responses.add(
        responses.GET,
        f"{DEFAULT_BASE_URL}/countries",
        json=SAMPLE_COUNTRIES,
        status=200,
    )
    countries = client.get_countries()
    assert "us" in countries
    assert countries["us"].name == "United States"


@responses.activate
def test_get_country(client):
    responses.add(
        responses.GET,
        f"{DEFAULT_BASE_URL}/countries/us",
        json=SAMPLE_COUNTRY,
        status=200,
    )
    country = client.get_country("us")
    assert country.country_code == "us"


@responses.activate
def test_get_genres(client):
    responses.add(
        responses.GET,
        f"{DEFAULT_BASE_URL}/genres",
        json=SAMPLE_GENRES,
        status=200,
    )
    genres = client.get_genres()
    assert genres["action"].name == "Action"


@responses.activate
def test_search_shows_by_filters_serializes_arrays(client):
    responses.add(
        responses.GET,
        f"{DEFAULT_BASE_URL}/shows/search/filters",
        json=SAMPLE_SEARCH_RESULT,
        status=200,
    )
    result = client.search_shows_by_filters(
        country="us",
        catalogs=["netflix", "hbo"],
        genres=["drama", "action"],
        year_min=1990,
        year_max=2000,
    )
    assert result.has_more is True
    assert result.next_cursor == "abc123"
    sent = responses.calls[0].request
    assert "catalogs=netflix%2Chbo" in sent.url or "catalogs=netflix,hbo" in sent.url
    assert "genres=drama%2Caction" in sent.url or "genres=drama,action" in sent.url
    assert "year_min=1990" in sent.url
    assert "year_max=2000" in sent.url


@responses.activate
def test_search_shows_by_title(client):
    responses.add(
        responses.GET,
        f"{DEFAULT_BASE_URL}/shows/search/title",
        json=SAMPLE_SEARCH_RESULT,
        status=200,
    )
    result = client.search_shows_by_title(title="Shawshank", country="us")
    assert len(result.shows) == 1
    sent = responses.calls[0].request
    assert "title=Shawshank" in sent.url
    assert "country=us" in sent.url


@responses.activate
def test_get_top_shows(client):
    responses.add(
        responses.GET,
        f"{DEFAULT_BASE_URL}/shows/top",
        json=SAMPLE_SEARCH_RESULT,
        status=200,
    )
    result = client.get_top_shows(country="us", service="netflix")
    assert len(result.shows) == 1


@responses.activate
def test_get_changes(client):
    responses.add(
        responses.GET,
        f"{DEFAULT_BASE_URL}/changes",
        json=SAMPLE_CHANGES_RESULT,
        status=200,
    )
    result = client.get_changes(country="us", change_type="new", item_type="show")
    assert len(result.changes) == 1
    assert result.shows["tt0111161"].title == "The Shawshank Redemption"


@responses.activate
def test_404_raises_not_found_error(client):
    responses.add(
        responses.GET,
        f"{DEFAULT_BASE_URL}/shows/nonexistent",
        json=ERROR_NOT_FOUND,
        status=404,
    )
    with pytest.raises(NotFoundError) as exc_info:
        client.get_show("nonexistent")
    assert exc_info.value.message == "Show not found"
    assert exc_info.value.status_code == 404


@responses.activate
def test_429_raises_rate_limit_error(client):
    responses.add(
        responses.GET,
        f"{DEFAULT_BASE_URL}/shows/tt0111161",
        json={"message": "Too many requests"},
        status=429,
    )
    with pytest.raises(RateLimitError):
        client.get_show("tt0111161")


@responses.activate
def test_none_params_are_not_sent(client):
    responses.add(
        responses.GET,
        f"{DEFAULT_BASE_URL}/shows/tt0111161",
        json=SAMPLE_SHOW,
        status=200,
    )
    client.get_show("tt0111161")
    sent = responses.calls[0].request
    assert "country=" not in sent.url
    assert "series_granularity=" not in sent.url


def test_custom_session_is_used():
    import requests

    session = requests.Session()
    client = StreamingAvailabilityClient(api_key="key", session=session)
    assert client._session is session
