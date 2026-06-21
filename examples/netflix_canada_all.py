"""Fetch ALL Netflix shows available in Canada by paginating automatically.

Loops using `next_cursor` until either:
  - `has_more` is False (we've genuinely reached the end), or
  - the API rate limit is hit (RateLimitError), in which case we stop
    early instead of crashing, and print the cursor you need to resume
    from once your limit resets.

Run with:
    STREAMING_AVAILABILITY_API_KEY=your_key python examples/netflix_canada_all.py

To resume after a rate limit, pass the cursor it printed last time:
    STREAMING_AVAILABILITY_API_KEY=your_key python examples/netflix_canada_all.py "PREVIOUS_CURSOR_VALUE"
"""

import os
import sys
from typing import List, Optional

from streaming_availability import RateLimitError, StreamingAvailabilityClient
from streaming_availability.models import Show


def fetch_all_netflix_canada_shows(
    client: StreamingAvailabilityClient,
    cursor: Optional[str] = None,
) -> List[Show]:
    all_shows: List[Show] = []
    page = 1

    while True:
        try:
            result = client.search_shows_by_filters(
                country="ca",
                catalogs=["netflix"],
                cursor=cursor,
            )
        except RateLimitError as e:
            print()
            print(f"Hit the API rate limit on page {page}: {e}")
            print(f"Stopping early. Resume later with cursor: {cursor!r}")
            break

        all_shows.extend(result.shows)
        print(
            f"Page {page}: got {len(result.shows)} shows, "
            f"next_cursor -> {result.next_cursor!r}"
        )

        if not result.has_more:
            print("Reached the end of the results (has_more is False).")
            break

        cursor = result.next_cursor
        page += 1

    return all_shows


def main() -> None:
    api_key = os.environ["STREAMING_AVAILABILITY_API_KEY"]

    # Optional: resume from a cursor saved from a previous (rate-limited) run.
    starting_cursor = sys.argv[1] if len(sys.argv) > 1 else None

    with StreamingAvailabilityClient(api_key=api_key) as client:
        shows = fetch_all_netflix_canada_shows(client, cursor=starting_cursor)

    print()
    print(f"Total Netflix CA shows fetched this run: {len(shows)}")
    for show in shows[:10]:
        print(f"  - {show.title} ({show.release_year})")
    if len(shows) > 10:
        print(f"  ...and {len(shows) - 10} more")


if __name__ == "__main__":
    main()
