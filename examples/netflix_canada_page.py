"""Fetch one page of Netflix shows available in Canada and write the FULL
raw API data to a JSON file (not just title/year -- every field the API
returns for each show: cast, genres, full streaming options with prices,
qualities, subtitles, seasons/episodes if present, etc).

Each call to `search_shows_by_filters` returns up to a page of shows plus:
  - has_more: bool, whether there are more results
  - next_cursor: str | None, pass this back in as `cursor=...` to get the next page

This script fetches ONE page and writes it to a JSON file. The output file
also stores `has_more`/`next_cursor` so it's self-contained -- you (or
another script) can read it back later to know exactly where to resume.

Run with:
    STREAMING_AVAILABILITY_API_KEY=your_key python examples/netflix_canada_page.py

Optionally pass a cursor from a previous run to get the next page:
    STREAMING_AVAILABILITY_API_KEY=your_key python examples/netflix_canada_page.py "PREVIOUS_CURSOR_VALUE"

Optionally pass an output path as the second arg (default: netflix_ca_page.json):
    STREAMING_AVAILABILITY_API_KEY=your_key python examples/netflix_canada_page.py "" my_output.json
"""

import json
import os
import sys

from streaming_availability import StreamingAvailabilityClient


def main() -> None:
    api_key = os.environ["STREAMING_AVAILABILITY_API_KEY"]

    # Optional: pass the cursor from a previous run as the first CLI arg
    # to continue where you left off. Pass "" to skip it and just set an
    # output path as the second arg.
    cursor = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else None
    output_path = sys.argv[2] if len(sys.argv) > 2 else "netflix_ca_page.json"

    with StreamingAvailabilityClient(api_key=api_key) as client:
        result = client.search_shows_by_filters(
            country="ca",
            catalogs=["netflix"],
            cursor=cursor,
        )

    # result.shows is a list of Show objects; .raw on each one is the
    # complete, untouched JSON object the API returned for that show --
    # this is what gets written out, not just the few fields exposed as
    # convenience properties (title, release_year, etc).
    output_data = {
        "has_more": result.has_more,
        "next_cursor": result.next_cursor,
        "show_count": len(result.shows),
        "shows": [show.raw for show in result.shows],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(result.shows)} full show records to {output_path}")
    print(f"has_more:    {result.has_more}")
    print(f"next_cursor: {result.next_cursor!r}")

    if result.has_more:
        print()
        print("To get the next page, run:")
        print(
            f'  STREAMING_AVAILABILITY_API_KEY=*** python {sys.argv[0]} '
            f'"{result.next_cursor}"'
        )


if __name__ == "__main__":
    main()
