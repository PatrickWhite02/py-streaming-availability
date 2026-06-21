"""Enumerations for the fixed-value fields used throughout the Streaming
Availability API.

These all subclass ``str`` so they can be passed directly wherever the API
expects a plain string (e.g. as a query parameter value or compared against
a JSON field), while still giving you autocomplete and a single source of
truth for the valid values.
"""

from __future__ import annotations

from enum import Enum


class ShowType(str, Enum):
    """Type of a show."""

    MOVIE = "movie"
    SERIES = "series"


class ItemType(str, Enum):
    """Type of an item referenced by a change."""

    SHOW = "show"
    SEASON = "season"
    EPISODE = "episode"


class ChangeType(str, Enum):
    """Type of a catalog change."""

    NEW = "new"
    REMOVED = "removed"
    UPDATED = "updated"
    EXPIRING = "expiring"
    UPCOMING = "upcoming"


class OrderDirection(str, Enum):
    """Sort direction used by endpoints that support ordering."""

    ASC = "asc"
    DESC = "desc"


class GenresRelation(str, Enum):
    """How multiple genre filters should be combined."""

    AND = "and"
    OR = "or"


class SearchFiltersOrderBy(str, Enum):
    """Sort key for :meth:`search_shows_by_filters`."""

    ORIGINAL_TITLE = "original_title"
    RELEASE_DATE = "release_date"
    RATING = "rating"
    POPULARITY_ALLTIME = "popularity_alltime"
    POPULARITY_1YEAR = "popularity_1year"
    POPULARITY_1MONTH = "popularity_1month"
    POPULARITY_1WEEK = "popularity_1week"


class SeriesGranularity(str, Enum):
    """How much season/episode detail to include for series."""

    SHOW = "show"
    SEASON = "season"
    EPISODE = "episode"


class OutputLanguage(str, Enum):
    """Supported output languages.

    This is a convenience enum for the languages the API documents as
    supported. Any ISO 639-1 string is still accepted by the client even
    if it isn't listed here, in case the API adds more languages later.
    """

    EN = "en"
    ES = "es"
    TR = "tr"
    FR = "fr"


class StreamingOptionQuality(str, Enum):
    """Maximum supported video quality of a streaming option."""

    SD = "sd"
    HD = "hd"
    QHD = "qhd"
    UHD = "uhd"


class StreamingOptionTypeValue(str, Enum):
    """The way a show is offered through a streaming option."""

    SUBSCRIPTION = "subscription"
    FREE = "free"
    RENT = "rent"
    BUY = "buy"
    ADDON = "addon"
