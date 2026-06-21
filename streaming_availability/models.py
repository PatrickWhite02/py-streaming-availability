"""Typed wrappers around the JSON objects returned by the API.

Every model wraps the raw ``dict`` returned by the API (available via
``.raw``) and exposes its fields as typed properties. This keeps the
library resilient to the API adding new fields in the future -- nothing
breaks, you just won't see the new field as a property until the library
is updated, but you can always reach it via ``.raw["newField"]``.

None of these classes need to be constructed by hand; they're built for
you from the responses returned by :class:`~streaming_availability.client.StreamingAvailabilityClient`
and :class:`~streaming_availability.client.AsyncStreamingAvailabilityClient`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class _Model:
    """Base class for all response models.

    Wraps a raw dict and provides equality/repr based on it.
    """

    __slots__ = ("raw",)

    def __init__(self, raw: Dict[str, Any]) -> None:
        self.raw = raw

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.raw!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Model):
            return self.raw == other.raw
        return NotImplemented

    def to_dict(self) -> Dict[str, Any]:
        """Return the original, unmodified JSON object as a dict."""
        return self.raw


class ImageSet(_Model):
    """A set of logo images in different shapes, e.g. for a service or addon."""

    @property
    def light_theme_image(self) -> Optional[str]:
        return self.raw.get("lightThemeImage")

    @property
    def dark_theme_image(self) -> Optional[str]:
        return self.raw.get("darkThemeImage")

    @property
    def white_image(self) -> Optional[str]:
        return self.raw.get("whiteImage")


class Addon(_Model):
    """Details of an addon (e.g. Apple TV Channels, Prime Video Channels)."""

    @property
    def id(self) -> str:
        return self.raw["id"]

    @property
    def name(self) -> str:
        return self.raw["name"]

    @property
    def home_page(self) -> str:
        return self.raw["homePage"]

    @property
    def theme_color_code(self) -> str:
        return self.raw["themeColorCode"]

    @property
    def image_set(self) -> ImageSet:
        return ImageSet(self.raw["imageSet"])


class ServiceInfo(_Model):
    """Information about the streaming service for a particular streaming option."""

    @property
    def id(self) -> str:
        return self.raw["id"]

    @property
    def name(self) -> str:
        return self.raw["name"]

    @property
    def home_page(self) -> str:
        return self.raw.get("homePage", "")

    @property
    def theme_color_code(self) -> str:
        return self.raw.get("themeColorCode", "")

    @property
    def image_set(self) -> Optional[ImageSet]:
        image_set = self.raw.get("imageSet")
        return ImageSet(image_set) if image_set is not None else None


class Service(_Model):
    """A streaming service available in a country (as returned by /countries)."""

    @property
    def id(self) -> str:
        return self.raw["id"]

    @property
    def name(self) -> str:
        return self.raw["name"]

    @property
    def home_page(self) -> str:
        return self.raw.get("homePage", "")

    @property
    def theme_color_code(self) -> str:
        return self.raw.get("themeColorCode", "")

    @property
    def image_set(self) -> Optional[ImageSet]:
        image_set = self.raw.get("imageSet")
        return ImageSet(image_set) if image_set is not None else None

    @property
    def streaming_option_types(self) -> Dict[str, bool]:
        return self.raw.get("streamingOptionTypes", {})

    @property
    def addons(self) -> List[Addon]:
        return [Addon(a) for a in self.raw.get("addons", [])]


class Locale(_Model):
    """A language/locale entry, e.g. for an available audio track."""

    @property
    def language(self) -> str:
        return self.raw["language"]

    @property
    def region(self) -> Optional[str]:
        return self.raw.get("region")


class Subtitle(_Model):
    """A subtitle track available for a streaming option."""

    @property
    def closed_captions(self) -> bool:
        return self.raw.get("closedCaptions", False)

    @property
    def locale(self) -> Locale:
        return Locale(self.raw["locale"])


class Price(_Model):
    """Price of a buyable/rentable streaming option."""

    @property
    def amount(self) -> str:
        return self.raw["amount"]

    @property
    def currency(self) -> str:
        return self.raw["currency"]

    @property
    def formatted(self) -> str:
        return self.raw.get("formatted", "")


class StreamingOption(_Model):
    """A single way to watch a show/season/episode (e.g. on Netflix via subscription)."""

    @property
    def service(self) -> ServiceInfo:
        return ServiceInfo(self.raw["service"])

    @property
    def type(self) -> str:
        """One of ``subscription``, ``free``, ``rent``, ``buy``, or ``addon``."""
        return self.raw["type"]

    @property
    def addon(self) -> Optional[Addon]:
        addon = self.raw.get("addon")
        return Addon(addon) if addon is not None else None

    @property
    def link(self) -> str:
        return self.raw["link"]

    @property
    def video_link(self) -> Optional[str]:
        return self.raw.get("videoLink")

    @property
    def quality(self) -> Optional[str]:
        return self.raw.get("quality")

    @property
    def audios(self) -> List[Locale]:
        return [Locale(a) for a in self.raw.get("audios", [])]

    @property
    def subtitles(self) -> List[Subtitle]:
        return [Subtitle(s) for s in self.raw.get("subtitles", [])]

    @property
    def price(self) -> Optional[Price]:
        price = self.raw.get("price")
        return Price(price) if price is not None else None

    @property
    def expires_soon(self) -> bool:
        return self.raw.get("expiresSoon", False)

    @property
    def expires_on(self) -> Optional[int]:
        return self.raw.get("expiresOn")

    @property
    def available_since(self) -> Optional[int]:
        return self.raw.get("availableSince")


def _streaming_options_map(raw: Dict[str, List[dict]]) -> Dict[str, List[StreamingOption]]:
    """Convert a raw ``{countryCode: [streamingOption, ...]}`` map into models."""
    return {
        country: [StreamingOption(o) for o in options]
        for country, options in raw.items()
    }


class Episode(_Model):
    """An episode of a season, including its own streaming options."""

    @property
    def id(self) -> str:
        return self.raw["id"]

    @property
    def title(self) -> str:
        return self.raw["title"]

    @property
    def overview(self) -> Optional[str]:
        return self.raw.get("overview")

    @property
    def episode_number(self) -> int:
        return self.raw["episodeNumber"]

    @property
    def season_number(self) -> int:
        return self.raw["seasonNumber"]

    @property
    def release_date(self) -> Optional[str]:
        return self.raw.get("releaseDate")

    @property
    def image_set(self) -> Optional[Dict[str, Any]]:
        return self.raw.get("imageSet")

    @property
    def streaming_options(self) -> Dict[str, List[StreamingOption]]:
        return _streaming_options_map(self.raw.get("streamingOptions", {}))


class Season(_Model):
    """A season of a series, optionally including its episodes."""

    @property
    def season_number(self) -> int:
        return self.raw["seasonNumber"]

    @property
    def episode_count(self) -> Optional[int]:
        return self.raw.get("episodeCount")

    @property
    def image_set(self) -> Optional[Dict[str, Any]]:
        return self.raw.get("imageSet")

    @property
    def episodes(self) -> List[Episode]:
        return [Episode(e) for e in self.raw.get("episodes", [])]

    @property
    def streaming_options(self) -> Dict[str, List[StreamingOption]]:
        return _streaming_options_map(self.raw.get("streamingOptions", {}))


class Show(_Model):
    """A movie or series, including its streaming availability.

    ``show_type`` tells you whether this is a ``"movie"`` or a ``"series"``;
    ``season_count``/``episode_count``/``seasons`` are only populated for series.
    """

    @property
    def id(self) -> str:
        return self.raw["id"]

    @property
    def imdb_id(self) -> Optional[str]:
        return self.raw.get("imdbId")

    @property
    def tmdb_id(self) -> Optional[str]:
        return self.raw.get("tmdbId")

    @property
    def title(self) -> str:
        return self.raw["title"]

    @property
    def show_type(self) -> str:
        """``"movie"`` or ``"series"``."""
        return self.raw["showType"]

    @property
    def is_movie(self) -> bool:
        return self.show_type == "movie"

    @property
    def is_series(self) -> bool:
        return self.show_type == "series"

    @property
    def overview(self) -> Optional[str]:
        return self.raw.get("overview")

    @property
    def release_year(self) -> Optional[int]:
        return self.raw.get("releaseYear")

    @property
    def first_air_year(self) -> Optional[int]:
        return self.raw.get("firstAirYear")

    @property
    def last_air_year(self) -> Optional[int]:
        return self.raw.get("lastAirYear")

    @property
    def original_title(self) -> Optional[str]:
        return self.raw.get("originalTitle")

    @property
    def genres(self) -> List["Genre"]:
        return [Genre(g) for g in self.raw.get("genres", [])]

    @property
    def directors(self) -> List[str]:
        return self.raw.get("directors", [])

    @property
    def cast(self) -> List[str]:
        return self.raw.get("cast", [])

    @property
    def rating(self) -> Optional[int]:
        return self.raw.get("rating")

    @property
    def image_set(self) -> Optional[Dict[str, Any]]:
        return self.raw.get("imageSet")

    @property
    def season_count(self) -> Optional[int]:
        return self.raw.get("seasonCount")

    @property
    def episode_count(self) -> Optional[int]:
        return self.raw.get("episodeCount")

    @property
    def seasons(self) -> List[Season]:
        return [Season(s) for s in self.raw.get("seasons", [])]

    @property
    def streaming_options(self) -> Dict[str, List[StreamingOption]]:
        """Map of country code -> list of streaming options in that country."""
        return _streaming_options_map(self.raw.get("streamingOptions", {}))


class Genre(_Model):
    """A genre used to categorize shows."""

    @property
    def id(self) -> str:
        return self.raw["id"]

    @property
    def name(self) -> str:
        return self.raw["name"]


class Country(_Model):
    """A country supported by the API, with its available streaming services."""

    @property
    def country_code(self) -> str:
        return self.raw["countryCode"]

    @property
    def name(self) -> str:
        return self.raw["name"]

    @property
    def services(self) -> List[Service]:
        return [Service(s) for s in self.raw.get("services", [])]


class Change(_Model):
    """A past or future change in a streaming catalog (new/removed/updated/etc.)."""

    @property
    def change_type(self) -> str:
        return self.raw["changeType"]

    @property
    def item_type(self) -> str:
        return self.raw["itemType"]

    @property
    def show_id(self) -> str:
        return self.raw["showId"]

    @property
    def season_number(self) -> Optional[int]:
        return self.raw.get("seasonNumber")

    @property
    def episode_number(self) -> Optional[int]:
        return self.raw.get("episodeNumber")

    @property
    def country(self) -> Optional[str]:
        return self.raw.get("country")

    @property
    def service_id(self) -> Optional[str]:
        return self.raw.get("serviceId")

    @property
    def timestamp(self) -> Optional[int]:
        return self.raw.get("timestamp")


class SearchResult(_Model):
    """A page of results from the show-search endpoints."""

    @property
    def shows(self) -> List[Show]:
        return [Show(s) for s in self.raw.get("shows", [])]

    @property
    def has_more(self) -> bool:
        return self.raw.get("hasMore", False)

    @property
    def next_cursor(self) -> Optional[str]:
        return self.raw.get("nextCursor")


class ChangesResult(_Model):
    """A page of results from the /changes endpoint."""

    @property
    def changes(self) -> List[Change]:
        return [Change(c) for c in self.raw.get("changes", [])]

    @property
    def shows(self) -> Dict[str, Show]:
        """Map of show id -> :class:`Show`, for shows affected by ``changes``."""
        return {show_id: Show(s) for show_id, s in self.raw.get("shows", {}).items()}

    @property
    def has_more(self) -> bool:
        return self.raw.get("hasMore", False)

    @property
    def next_cursor(self) -> Optional[str]:
        return self.raw.get("nextCursor")
