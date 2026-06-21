from streaming_availability._base import (
    DEFAULT_BASE_URL,
    RAPIDAPI_BASE_URL,
    build_auth_headers,
    build_query_params,
    raise_for_error_response,
)
from streaming_availability.enums import ShowType
from streaming_availability.exceptions import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
    ServerError,
    StreamingAvailabilityError,
)

import pytest


def test_build_query_params_drops_none():
    assert build_query_params({"a": None, "b": "x"}) == {"b": "x"}


def test_build_query_params_bool():
    assert build_query_params({"flag": True}) == {"flag": "true"}
    assert build_query_params({"flag": False}) == {"flag": "false"}


def test_build_query_params_enum():
    assert build_query_params({"show_type": ShowType.MOVIE}) == {"show_type": "movie"}


def test_build_query_params_list_join():
    assert build_query_params({"catalogs": ["netflix", "hbo"]}) == {
        "catalogs": "netflix,hbo"
    }


def test_build_query_params_empty_list_dropped():
    assert build_query_params({"catalogs": []}) == {}


def test_build_query_params_int():
    assert build_query_params({"year_min": 1999}) == {"year_min": "1999"}


def test_build_auth_headers_default():
    assert build_auth_headers("secret", False) == {"X-API-Key": "secret"}


def test_build_auth_headers_rapidapi():
    assert build_auth_headers("secret", True) == {"X-RapidAPI-Key": "secret"}


def test_base_urls_differ():
    assert DEFAULT_BASE_URL != RAPIDAPI_BASE_URL


@pytest.mark.parametrize(
    "status_code,expected_exc",
    [
        (400, BadRequestError),
        (401, AuthenticationError),
        (403, AuthenticationError),
        (404, NotFoundError),
        (429, RateLimitError),
        (500, ServerError),
        (503, ServerError),
        (418, StreamingAvailabilityError),
    ],
)
def test_raise_for_error_response_maps_status_codes(status_code, expected_exc):
    with pytest.raises(expected_exc) as exc_info:
        raise_for_error_response(
            status_code, {"message": "boom"}, url="https://example.com"
        )
    assert exc_info.value.status_code == status_code
    assert exc_info.value.message == "boom"


def test_raise_for_error_response_success_is_noop():
    raise_for_error_response(200, {"ok": True}, url="https://example.com")  # no raise


def test_error_str_includes_status_code():
    err = StreamingAvailabilityError("bad", status_code=404)
    assert str(err) == "[404] bad"
