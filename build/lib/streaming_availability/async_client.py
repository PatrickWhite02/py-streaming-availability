"""Asynchronous client for the Streaming Availability API, built on ``httpx``.

``httpx`` is an optional dependency. Install it with::

    pip install streaming-availability[async]

or simply::

    pip install httpx

This module can be imported even without ``httpx`` installed; the
:class:`ImportError` is only raised when you actually try to instantiate
:class:`AsyncStreamingAvailabilityClient`, so importing the top-level
``streaming_availability`` package never requires ``httpx``.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional, Union

from . import _endpoints as ep
from ._base import (
    DEFAULT_BASE_URL,
    RAPIDAPI_BASE_URL,
    build_auth_headers,
    raise_for_error_response,
)
from .enums import (
    ChangeType,
    GenresRelation,
    ItemType,
    OrderDirection,
    SearchFiltersOrderBy,
    SeriesGranularity,
    ShowType,
)
from .models import ChangesResult, Country, Genre, SearchResult, Show

try:
    import httpx
except ImportError:  # pragma: no cover - exercised via the no-httpx test env
    httpx = None  # type: ignore[assignment]

_HTTPX_INSTALL_HINT = (
    "AsyncStreamingAvailabilityClient requires the 'httpx' package. "
    "Install it with `pip install streaming-availability[async]` "
    "or `pip install httpx`."
)


class AsyncStreamingAvailabilityClient:
    """Asynchronous client for the Streaming Availability API.

    Mirrors :class:`~streaming_availability.client.StreamingAvailabilityClient`
    method-for-method, just with ``async def``/``await``. Requires the
    optional ``httpx`` dependency -- see the module docstring.

    Example:
        >>> async with AsyncStreamingAvailabilityClient(api_key="...") as client:
        ...     show = await client.get_show("tt0111161")
        ...     print(show.title)

    Args:
        api_key: Your API key, from either developers.movieofthenight.com
            or rapidapi.com.
        use_rapidapi: Set to ``True`` if ``api_key`` came from rapidapi.com.
            This switches both the auth header and the default base URL.
        base_url: Override the server URL entirely. Mainly useful for
            testing against a mock server.
        client: Optionally supply your own ``httpx.AsyncClient``. One is
            created for you otherwise.
        timeout: Default timeout (seconds) applied to every request unless
            overridden by your own ``client``.
    """

    def __init__(
        self,
        api_key: str,
        *,
        use_rapidapi: bool = False,
        base_url: Optional[str] = None,
        client: Optional["httpx.AsyncClient"] = None,
        timeout: float = 10.0,
    ) -> None:
        if httpx is None:
            raise ImportError(_HTTPX_INSTALL_HINT)
        if not api_key:
            raise ValueError("api_key is required")

        self.api_key = api_key
        self.use_rapidapi = use_rapidapi
        self.base_url = (
            base_url
            if base_url is not None
            else (RAPIDAPI_BASE_URL if use_rapidapi else DEFAULT_BASE_URL)
        ).rstrip("/")
        self._client = client or httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        """Close the underlying ``httpx.AsyncClient``."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncStreamingAvailabilityClient":
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    # -- low-level request plumbing -----------------------------------

    async def _request(self, method: str, path: str, params: dict) -> Any:
        url = f"{self.base_url}{path}"
        headers = build_auth_headers(self.api_key, self.use_rapidapi)
        response = await self._client.request(
            method, url, params=params, headers=headers
        )
        try:
            body = response.json() if response.content else None
        except ValueError:
            body = None
        raise_for_error_response(response.status_code, body, url=url)
        return body

    # -- endpoints -------------------------------------------------------

    async def get_countries(self, *, output_language: Optional[str] = None) -> dict:
        """Get all supported countries and their streaming services.

        Returns:
            A dict mapping country code to a :class:`~streaming_availability.models.Country`.
        """
        method, path, params = ep.get_countries(output_language=output_language)
        body = await self._request(method, path, params)
        return {code: Country(c) for code, c in body.items()}

    async def get_country(
        self, country_code: str, *, output_language: Optional[str] = None
    ) -> Country:
        """Get a single country and its supported streaming services."""
        method, path, params = ep.get_country(
            country_code, output_language=output_language
        )
        body = await self._request(method, path, params)
        return Country(body)

    async def get_genres(self, *, output_language: Optional[str] = None) -> dict:
        """Get all genres available for filtering shows.

        Returns:
            A dict mapping genre id to a :class:`~streaming_availability.models.Genre`.
        """
        method, path, params = ep.get_genres(output_language=output_language)
        body = await self._request(method, path, params)
        return {genre_id: Genre(g) for genre_id, g in body.items()}

    async def get_show(
        self,
        show_id: str,
        *,
        country: Optional[str] = None,
        series_granularity: Optional[Union[str, SeriesGranularity]] = None,
        output_language: Optional[str] = None,
    ) -> Show:
        """Get a single show by its id (also accepts IMDb and TMDB ids)."""
        method, path, params = ep.get_show(
            show_id,
            country=country,
            series_granularity=series_granularity,
            output_language=output_language,
        )
        body = await self._request(method, path, params)
        return Show(body)

    async def search_shows_by_filters(
        self,
        *,
        country: str,
        catalogs: Optional[Iterable[str]] = None,
        output_language: Optional[str] = None,
        show_type: Optional[Union[str, ShowType]] = None,
        genres: Optional[Iterable[str]] = None,
        genres_relation: Optional[Union[str, GenresRelation]] = None,
        show_original_language: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        rating_min: Optional[int] = None,
        rating_max: Optional[int] = None,
        keyword: Optional[str] = None,
        series_granularity: Optional[Union[str, SeriesGranularity]] = None,
        order_by: Optional[Union[str, SearchFiltersOrderBy]] = None,
        order_direction: Optional[Union[str, OrderDirection]] = None,
        cursor: Optional[str] = None,
    ) -> SearchResult:
        """Search shows by filters such as genre, year, rating, catalogs, etc."""
        method, path, params = ep.search_shows_by_filters(
            country=country,
            catalogs=catalogs,
            output_language=output_language,
            show_type=show_type,
            genres=genres,
            genres_relation=genres_relation,
            show_original_language=show_original_language,
            year_min=year_min,
            year_max=year_max,
            rating_min=rating_min,
            rating_max=rating_max,
            keyword=keyword,
            series_granularity=series_granularity,
            order_by=order_by,
            order_direction=order_direction,
            cursor=cursor,
        )
        body = await self._request(method, path, params)
        return SearchResult(body)

    async def search_shows_by_title(
        self,
        *,
        title: str,
        country: str,
        show_type: Optional[Union[str, ShowType]] = None,
        series_granularity: Optional[Union[str, SeriesGranularity]] = None,
        output_language: Optional[str] = None,
    ) -> SearchResult:
        """Search shows by title."""
        method, path, params = ep.search_shows_by_title(
            title=title,
            country=country,
            show_type=show_type,
            series_granularity=series_granularity,
            output_language=output_language,
        )
        body = await self._request(method, path, params)
        return SearchResult(body)

    async def get_top_shows(
        self,
        *,
        country: str,
        service: str,
        output_language: Optional[str] = None,
        show_type: Optional[Union[str, ShowType]] = None,
    ) -> SearchResult:
        """Get the top shows currently on a given service in a given country."""
        method, path, params = ep.get_top_shows(
            country=country,
            service=service,
            output_language=output_language,
            show_type=show_type,
        )
        body = await self._request(method, path, params)
        return SearchResult(body)

    async def get_changes(
        self,
        *,
        country: str,
        change_type: Union[str, ChangeType],
        item_type: Union[str, ItemType],
        catalogs: Optional[Iterable[str]] = None,
        show_type: Optional[Union[str, ShowType]] = None,
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
        include_unknown_dates: Optional[bool] = None,
        cursor: Optional[str] = None,
        order_direction: Optional[Union[str, OrderDirection]] = None,
        output_language: Optional[str] = None,
    ) -> ChangesResult:
        """Get recent or upcoming changes (new/removed/updated/expiring/upcoming)."""
        method, path, params = ep.get_changes(
            country=country,
            change_type=change_type,
            item_type=item_type,
            catalogs=catalogs,
            show_type=show_type,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            include_unknown_dates=include_unknown_dates,
            cursor=cursor,
            order_direction=order_direction,
            output_language=output_language,
        )
        body = await self._request(method, path, params)
        return ChangesResult(body)
