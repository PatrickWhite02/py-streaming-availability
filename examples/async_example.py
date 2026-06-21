"""Async usage example. Requires the optional `httpx` extra:

    pip install streaming-availability[async]

Run with:
    STREAMING_AVAILABILITY_API_KEY=your_key python examples/async_example.py

This example also shows the main motivation for the async client: running
it concurrently alongside other async API calls (here, a couple of plain
`httpx` requests standing in for "other api libs") instead of blocking
your event loop with a sync HTTP call.
"""

import asyncio
import os

import httpx

from streaming_availability import AsyncStreamingAvailabilityClient


async def fetch_show(client: AsyncStreamingAvailabilityClient, show_id: str):
    return await client.get_show(show_id, country="us")


async def fetch_something_else_entirely():
    # Stand-in for a call into some other async API client in your stack.
    async with httpx.AsyncClient() as http:
        response = await http.get("https://httpbin.org/json")
        return response.json()


async def main() -> None:
    api_key = os.environ["STREAMING_AVAILABILITY_API_KEY"]

    async with AsyncStreamingAvailabilityClient(api_key=api_key) as client:
        # Several calls to this library, and a call to something unrelated,
        # all running concurrently on the same event loop.
        show_ids = ["tt0111161", "tt0468569", "tt1375666"]
        shows, other_data = await asyncio.gather(
            asyncio.gather(*(fetch_show(client, sid) for sid in show_ids)),
            fetch_something_else_entirely(),
        )

        for show in shows:
            print(show.title, show.release_year)

        print("Other API call returned:", other_data)


if __name__ == "__main__":
    asyncio.run(main())
