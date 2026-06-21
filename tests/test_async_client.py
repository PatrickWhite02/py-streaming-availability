import httpx
import pytest
import respx

from streaming_availability import AsyncStreamingAvailabilityClient, NotFoundError
from streaming_availability._base import DEFAULT_BASE_URL, RAPIDAPI_BASE_URL

from .fixtures import ERROR_NOT_FOUND, SAMPLE_SEARCH_RESULT, SAMPLE_SHOW


@pytest.fixture
async def client():
    async with AsyncStreamingAvailabilityClient(api_key="test-key") as c:
        yield c


def test_requires_api_key():
    with pytest.raises(ValueError):
        AsyncStreamingAvailabilityClient(api_key="")


@respx.mock
async def test_get_show(client):
    route = respx.get(f"{DEFAULT_BASE_URL}/shows/tt0111161").mock(
        return_value=httpx.Response(200, json=SAMPLE_SHOW)
    )
    show = await client.get_show("tt0111161", country="us")

    assert show.title == "The Shawshank Redemption"
    assert route.called
    sent_request = route.calls[0].request
    assert sent_request.headers["x-api-key"] == "test-key"
    assert "country=us" in str(sent_request.url)


@respx.mock
async def test_rapidapi_header():
    client = AsyncStreamingAvailabilityClient(api_key="rapid-key", use_rapidapi=True)
    route = respx.get(f"{RAPIDAPI_BASE_URL}/shows/tt0111161").mock(
        return_value=httpx.Response(200, json=SAMPLE_SHOW)
    )
    await client.get_show("tt0111161")
    sent_request = route.calls[0].request
    assert sent_request.headers["x-rapidapi-key"] == "rapid-key"
    await client.aclose()


@respx.mock
async def test_search_shows_by_title(client):
    respx.get(f"{DEFAULT_BASE_URL}/shows/search/title").mock(
        return_value=httpx.Response(200, json=SAMPLE_SEARCH_RESULT)
    )
    result = await client.search_shows_by_title(title="Shawshank", country="us")
    assert len(result.shows) == 1
    assert result.shows[0].title == "The Shawshank Redemption"


@respx.mock
async def test_404_raises_not_found_error(client):
    respx.get(f"{DEFAULT_BASE_URL}/shows/nonexistent").mock(
        return_value=httpx.Response(404, json=ERROR_NOT_FOUND)
    )
    with pytest.raises(NotFoundError) as exc_info:
        await client.get_show("nonexistent")
    assert exc_info.value.message == "Show not found"


async def test_can_supply_custom_httpx_client():
    custom = httpx.AsyncClient()
    client = AsyncStreamingAvailabilityClient(api_key="key", client=custom)
    assert client._client is custom
    await client.aclose()
