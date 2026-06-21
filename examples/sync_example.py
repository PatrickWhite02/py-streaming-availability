"""Sync usage example. Requires only `requests`.

Run with:
    STREAMING_AVAILABILITY_API_KEY=your_key python examples/sync_example.py
"""

import os

from streaming_availability import StreamingAvailabilityClient


def main() -> None:
    api_key = os.environ["STREAMING_AVAILABILITY_API_KEY"]

    with StreamingAvailabilityClient(api_key=api_key) as client:
        show = client.get_show("tt0111161", country="us")
        print(f"{show.title} ({show.release_year}) - rating {show.rating}")

        for option in show.streaming_options.get("us", []):
            print(f"  - {option.service.name}: {option.type} -> {option.link}")

        print()
        print("Top movies on Netflix in the US:")
        top = client.get_top_shows(country="us", service="netflix", show_type="movie")
        for s in top.shows[:5]:
            print(f"  - {s.title}")


if __name__ == "__main__":
    main()
