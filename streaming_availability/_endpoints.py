"""Per-endpoint request specs, shared by the sync and async clients.

Each function here returns a ``(method, path, query_params)`` tuple for one
API operation. Keeping this logic in one place (rather than duplicated in
both client classes) means the sync and async clients are guaranteed to
build identical requests for identical inputs.
"""

from __future__ import annotations

from typing import Iterable, Optional, Union

from .enums import (
    ChangeType,
    GenresRelation,
    ItemType,
    OrderDirection,
    SearchFiltersOrderBy,
    SeriesGranularity,
    ShowType,
)
from ._base import QueryValue, build_query_params

EnumOrStr = Union[str, "object"]


def get_countries(*, output_language: Optional[str] = None):
    params = build_query_params({"output_language": output_language})
    return "GET", "/countries", params


def get_country(country_code: str, *, output_language: Optional[str] = None):
    params = build_query_params({"output_language": output_language})
    return "GET", f"/countries/{country_code}", params


def get_genres(*, output_language: Optional[str] = None):
    params = build_query_params({"output_language": output_language})
    return "GET", "/genres", params


def get_show(
    show_id: str,
    *,
    country: Optional[str] = None,
    series_granularity: Optional[Union[str, SeriesGranularity]] = None,
    output_language: Optional[str] = None,
):
    params = build_query_params(
        {
            "country": country,
            "series_granularity": series_granularity,
            "output_language": output_language,
        }
    )
    return "GET", f"/shows/{show_id}", params


def search_shows_by_filters(
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
):
    params = build_query_params(
        {
            "country": country,
            "catalogs": catalogs,
            "output_language": output_language,
            "show_type": show_type,
            "genres": genres,
            "genres_relation": genres_relation,
            "show_original_language": show_original_language,
            "year_min": year_min,
            "year_max": year_max,
            "rating_min": rating_min,
            "rating_max": rating_max,
            "keyword": keyword,
            "series_granularity": series_granularity,
            "order_by": order_by,
            "order_direction": order_direction,
            "cursor": cursor,
        }
    )
    return "GET", "/shows/search/filters", params


def search_shows_by_title(
    *,
    title: str,
    country: str,
    show_type: Optional[Union[str, ShowType]] = None,
    series_granularity: Optional[Union[str, SeriesGranularity]] = None,
    output_language: Optional[str] = None,
):
    params = build_query_params(
        {
            "title": title,
            "country": country,
            "show_type": show_type,
            "series_granularity": series_granularity,
            "output_language": output_language,
        }
    )
    return "GET", "/shows/search/title", params


def get_top_shows(
    *,
    country: str,
    service: str,
    output_language: Optional[str] = None,
    show_type: Optional[Union[str, ShowType]] = None,
):
    params = build_query_params(
        {
            "country": country,
            "service": service,
            "output_language": output_language,
            "show_type": show_type,
        }
    )
    return "GET", "/shows/top", params


def get_changes(
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
):
    params = build_query_params(
        {
            "country": country,
            "change_type": change_type,
            "item_type": item_type,
            "catalogs": catalogs,
            "show_type": show_type,
            "from": from_timestamp,
            "to": to_timestamp,
            "include_unknown_dates": include_unknown_dates,
            "cursor": cursor,
            "order_direction": order_direction,
            "output_language": output_language,
        }
    )
    return "GET", "/changes", params
