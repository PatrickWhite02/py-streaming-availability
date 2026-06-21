"""Exceptions raised by the Streaming Availability API client."""

from __future__ import annotations

from typing import Any


class StreamingAvailabilityError(Exception):
    """Base class for all errors raised by this library.

    Attributes:
        message: Human readable error message.
        status_code: HTTP status code of the response, if any.
        response_body: Parsed JSON body of the response, if any.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        if self.status_code is not None:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(StreamingAvailabilityError):
    """Raised when the API key is missing, invalid, or rejected (401/403)."""


class NotFoundError(StreamingAvailabilityError):
    """Raised when the requested resource doesn't exist (404).

    Most commonly raised by :meth:`get_show` and :meth:`get_country` when
    the given id / country code doesn't exist.
    """


class RateLimitError(StreamingAvailabilityError):
    """Raised when the API rate limit has been exceeded (429)."""


class BadRequestError(StreamingAvailabilityError):
    """Raised for malformed requests, e.g. invalid parameter values (400)."""


class ServerError(StreamingAvailabilityError):
    """Raised when the API returns a server-side error (5xx)."""
