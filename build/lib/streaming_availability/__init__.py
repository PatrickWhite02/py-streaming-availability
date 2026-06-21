"""Python client for the Streaming Availability API (movieofthenight.com).

Quick start (sync, requires only ``requests``)::

    from streaming_availability import StreamingAvailabilityClient

    client = StreamingAvailabilityClient(api_key="...")
    show = client.get_show("tt0111161")
    print(show.title)

Quick start (async, requires the optional ``httpx`` extra)::

    import asyncio
    from streaming_availability import AsyncStreamingAvailabilityClient

    async def main():
        async with AsyncStreamingAvailabilityClient(api_key="...") as client:
            show = await client.get_show("tt0111161")
            print(show.title)

    asyncio.run(main())

The async client is only imported lazily (see ``__getattr__`` below) so
that importing this package never requires ``httpx`` to be installed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .client import StreamingAvailabilityClient
from .enums import (
    ChangeType,
    GenresRelation,
    ItemType,
    OrderDirection,
    OutputLanguage,
    SearchFiltersOrderBy,
    SeriesGranularity,
    ShowType,
    StreamingOptionQuality,
    StreamingOptionTypeValue,
)
from .exceptions import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
    ServerError,
    StreamingAvailabilityError,
)
from .models import (
    Addon,
    Change,
    ChangesResult,
    Country,
    Episode,
    Genre,
    ImageSet,
    Locale,
    Price,
    SearchResult,
    Season,
    Service,
    ServiceInfo,
    Show,
    StreamingOption,
    Subtitle,
)

if TYPE_CHECKING:  # pragma: no cover
    from .async_client import AsyncStreamingAvailabilityClient

__version__ = "0.1.0"

__all__ = [
    "StreamingAvailabilityClient",
    "AsyncStreamingAvailabilityClient",
    # enums
    "ChangeType",
    "GenresRelation",
    "ItemType",
    "OrderDirection",
    "OutputLanguage",
    "SearchFiltersOrderBy",
    "SeriesGranularity",
    "ShowType",
    "StreamingOptionQuality",
    "StreamingOptionTypeValue",
    # exceptions
    "StreamingAvailabilityError",
    "AuthenticationError",
    "BadRequestError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    # models
    "Addon",
    "Change",
    "ChangesResult",
    "Country",
    "Episode",
    "Genre",
    "ImageSet",
    "Locale",
    "Price",
    "SearchResult",
    "Season",
    "Service",
    "ServiceInfo",
    "Show",
    "StreamingOption",
    "Subtitle",
]


def __getattr__(name: str):
    """Lazily import :class:`AsyncStreamingAvailabilityClient`.

    This keeps ``import streaming_availability`` working even when
    ``httpx`` isn't installed; the ``ImportError`` for a missing ``httpx``
    is only raised once you actually try to use the async client, with a
    message telling you how to install it.
    """
    if name == "AsyncStreamingAvailabilityClient":
        from .async_client import AsyncStreamingAvailabilityClient

        return AsyncStreamingAvailabilityClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
