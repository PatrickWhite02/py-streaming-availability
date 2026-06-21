"""Synchronous client for the Streaming Availability API, built on ``requests``."""

from __future__ import annotations

from typing import Any, Iterable, Optional, Union

import requests

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


class StreamingAvailabilityClient:
    """Synchronous client for the Streaming Availability API.

    Example:
        >>> client = StreamingAvailabilityClient(api_key="...")
        >>> show = client.get_show("tt0111161")
        >>> show.title
        'The Shawshank Redemption'

    Args:
        api_key: Your API key, from either developers.movieofthenight.com
            or rapidapi.com.
        use_rapidapi: Set to ``True`` if ``api_key`` came from rapidapi.com.
            This switches both the auth header and the default base URL.
        base_url: Override the server URL entirely. Mainly useful for
            testing against a mock server.
        session: Optionally supply your own ``requests.Session`` (e.g. one
            already configured with retries/proxies). One is created for
            you otherwise.
        timeout: Default timeout (seconds) applied to every request unless
            overridden per-call.
    """

    def __init__(
        self,
        api_key: str,
        *,
        use_rapidapi: bool = False,
        base_url: Optional[str] = None,
        session: Optional[requests.Session] = None,
        timeout: float = 10.0,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")

        self.api_key = api_key
        self.use_rapidapi = use_rapidapi
        self.base_url = (
            base_url
            if base_url is not None
            else (RAPIDAPI_BASE_URL if use_rapidapi else DEFAULT_BASE_URL)
        ).rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()

    def close(self) -> None:
        """Close the underlying ``requests.Session``."""
        self._session.close()

    def __enter__(self) -> "StreamingAvailabilityClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # -- low-level request plumbing -----------------------------------

    def _request(self, method: str, path: str, params: dict) -> Any:
        url = f"{self.base_url}{path}"
        headers = build_auth_headers(self.api_key, self.use_rapidapi)
        response = self._session.request(
            method,
            url,
            params=params,
            headers=headers,
            timeout=self.timeout,
        )
        try:
            body = response.json() if response.content else None
        except ValueError:
            body = None
        raise_for_error_response(response.status_code, body, url=url)
        return body

    # -- endpoints -------------------------------------------------------

    def get_countries(self, *, output_language: Optional[str] = None) -> dict:
        """Get all supported countries and their streaming services.

        Returns:
            A dict mapping country code to a :class:`~streaming_availability.models.Country`.
        """
        method, path, params = ep.get_countries(output_language=output_language)
        body = self._request(method, path, params)
        return {code: Country(c) for code, c in body.items()}

    def get_country(
        self, country_code: str, *, output_language: Optional[str] = None
    ) -> Country:
        """Get a single country and its supported streaming services."""
        method, path, params = ep.get_country(
            country_code, output_language=output_language
        )
        body = self._request(method, path, params)
        return Country(body)

    def get_genres(self, *, output_language: Optional[str] = None) -> dict:
        """Get all genres available for filtering shows.

        Returns:
            A dict mapping genre id to a :class:`~streaming_availability.models.Genre`.
        """
        method, path, params = ep.get_genres(output_language=output_language)
        body = self._request(method, path, params)
        return {genre_id: Genre(g) for genre_id, g in body.items()}

    def get_show(
        self,
        show_id: str,
        *,
        country: Optional[str] = None,
        series_granularity: Optional[Union[str, SeriesGranularity]] = None,
        output_language: Optional[str] = None,
    ) -> Show:
        """Get a single show by its id (also accepts IMDb and TMDB ids).

        Args:
            show_id: The show's id, IMDb id, or TMDB id (e.g. ``"tt0111161"``
                or ``"movie/278"``).
            country: Optional country code to also fetch streaming options for.
            series_granularity: How much season/episode detail to include
                for series (``"show"``, ``"season"``, or ``"episode"``).
            output_language: ISO 639-1 language code for text fields.
        """
        method, path, params = ep.get_show(
            show_id,
            country=country,
            series_granularity=series_granularity,
            output_language=output_language,
        )
        body = self._request(method, path, params)
        return Show(body)

    def search_shows_by_filters(
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
        """Search shows by filters such as genre, year, rating, catalogs, etc.

        Supports pagination via ``cursor``/``SearchResult.next_cursor``.

        Args:
            country: ISO 3166-1 alpha-2 country code to search in (required).
            catalogs: Catalog ids to restrict the search to, e.g.
                ``["netflix", "hbo"]``.
            show_type: Restrict to ``"movie"`` or ``"series"``.
            genres: Genre ids to filter by.
            genres_relation: ``"and"``/``"or"`` for combining multiple genres.
            show_original_language: ISO 639-1 code of the show's original language.
            year_min: Minimum release/air year.
            year_max: Maximum release/air year.
            rating_min: Minimum rating (0-100).
            rating_max: Maximum rating (0-100).
            keyword: Keyword to search for in overview/title.
            series_granularity: Season/episode detail level for series.
            order_by: Sort key, e.g. ``"rating"`` or ``"popularity_1year"``.
            order_direction: ``"asc"`` or ``"desc"``.
            cursor: Pagination cursor from a previous response.
        """
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
        body = self._request(method, path, params)
        return SearchResult(body)

    def search_shows_by_title(
        self,
        *,
        title: str,
        country: str,
        show_type: Optional[Union[str, ShowType]] = None,
        series_granularity: Optional[Union[str, SeriesGranularity]] = None,
        output_language: Optional[str] = None,
    ) -> SearchResult:
        """Search shows by title.

        Args:
            title: Title phrase to search for (required).
            country: ISO 3166-1 alpha-2 country code to search in (required).
            show_type: Restrict to ``"movie"`` or ``"series"``.
            series_granularity: Season/episode detail level for series.
            output_language: ISO 639-1 language code for text fields.
        """
        method, path, params = ep.search_shows_by_title(
            title=title,
            country=country,
            show_type=show_type,
            series_granularity=series_granularity,
            output_language=output_language,
        )
        body = self._request(method, path, params)
        return SearchResult(body)

    def get_top_shows(
        self,
        *,
        country: str,
        service: str,
        output_language: Optional[str] = None,
        show_type: Optional[Union[str, ShowType]] = None,
    ) -> SearchResult:
        """Get the top shows currently on a given service in a given country.

        Args:
            country: ISO 3166-1 alpha-2 country code (required).
            service: Id of the streaming service, e.g. ``"netflix"`` (required).
            show_type: Restrict to ``"movie"`` or ``"series"``.
        """
        method, path, params = ep.get_top_shows(
            country=country,
            service=service,
            output_language=output_language,
            show_type=show_type,
        )
        body = self._request(method, path, params)
        return SearchResult(body)

    def get_changes(
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
        """Get recent or upcoming changes (new/removed/updated/expiring/upcoming).

        Args:
            country: ISO 3166-1 alpha-2 country code (required).
            change_type: One of ``"new"``, ``"removed"``, ``"updated"``,
                ``"expiring"``, ``"upcoming"`` (required).
            item_type: One of ``"show"``, ``"season"``, ``"episode"`` (required).
            catalogs: Catalog ids to restrict the search to.
            show_type: Restrict to ``"movie"`` or ``"series"`` (only
                relevant when ``item_type="show"``).
            from_timestamp: Unix timestamp; only include changes at/after this.
            to_timestamp: Unix timestamp; only include changes at/before this.
            include_unknown_dates: Whether to include changes with unknown dates.
            cursor: Pagination cursor from a previous response.
            order_direction: ``"asc"`` or ``"desc"``.
        """
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
        body = self._request(method, path, params)
        return ChangesResult(body)
