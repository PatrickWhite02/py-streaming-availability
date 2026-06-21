"""Shared, transport-agnostic request building for the API clients.

Both the sync (:mod:`requests`-based) and async (:mod:`httpx`-based) clients
delegate URL/header/query-param construction to the helpers in this module,
so the two clients can never drift apart on how a request is built --
only on how it's actually sent.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Iterable, Mapping, Optional, Union

from .exceptions import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
    ServerError,
    StreamingAvailabilityError,
)

#: Default base URL for users with a key from developers.movieofthenight.com
DEFAULT_BASE_URL = "https://api.movieofthenight.com/v4"

#: Base URL for users with a key from rapidapi.com
RAPIDAPI_BASE_URL = "https://streaming-availability.p.rapidapi.com"

QueryValue = Union[str, int, float, bool, Enum, None]
QueryParam = Union[QueryValue, Iterable[QueryValue]]


def _coerce_scalar(value: QueryValue) -> Optional[str]:
    """Turn a single scalar query value into the string the API expects."""
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def build_query_params(params: Mapping[str, QueryParam]) -> Dict[str, str]:
    """Convert a dict of Pythonic parameter values into API-ready query params.

    - ``None`` values are dropped (so callers can pass every possible
      keyword argument and only the ones the user actually set get sent).
    - Enum members are unwrapped to their ``.value``.
    - Booleans become the literal strings ``"true"``/``"false"``.
    - Lists/tuples/sets are joined with commas, per this API's
      ``style: form, explode: false`` array parameters (e.g. ``catalogs``,
      ``genres``).
    """
    query: Dict[str, str] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple, set)):
            parts = [_coerce_scalar(v) for v in value if v is not None]
            non_empty_parts = [p for p in parts if p is not None]
            if not non_empty_parts:
                continue
            query[key] = ",".join(non_empty_parts)
        else:
            coerced = _coerce_scalar(value)  # type: ignore[arg-type]
            if coerced is not None:
                query[key] = coerced
    return query


def build_auth_headers(api_key: str, use_rapidapi: bool) -> Dict[str, str]:
    """Build the single auth header this API expects, based on the key source.

    The API accepts exactly one of ``X-API-Key`` (keys from
    developers.movieofthenight.com) or ``X-RapidAPI-Key`` (keys from
    rapidapi.com) -- never both.
    """
    if use_rapidapi:
        return {"X-RapidAPI-Key": api_key}
    return {"X-API-Key": api_key}


def raise_for_error_response(
    status_code: int,
    body: Any,
    *,
    url: str,
) -> None:
    """Raise the appropriate :class:`StreamingAvailabilityError` subclass.

    No-op if ``status_code`` indicates success.
    """
    if 200 <= status_code < 300:
        return

    message = f"Request to {url} failed with status {status_code}"
    if isinstance(body, dict) and "message" in body:
        message = body["message"]

    if status_code == 400:
        raise BadRequestError(message, status_code=status_code, response_body=body)
    if status_code in (401, 403):
        raise AuthenticationError(message, status_code=status_code, response_body=body)
    if status_code == 404:
        raise NotFoundError(message, status_code=status_code, response_body=body)
    if status_code == 429:
        raise RateLimitError(message, status_code=status_code, response_body=body)
    if status_code >= 500:
        raise ServerError(message, status_code=status_code, response_body=body)
    raise StreamingAvailabilityError(
        message, status_code=status_code, response_body=body
    )
