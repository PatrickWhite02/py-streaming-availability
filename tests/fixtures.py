"""Shared sample payloads used across the test suite."""

SAMPLE_SHOW = {
    "itemType": "show",
    "showType": "movie",
    "id": "tt0111161",
    "imdbId": "tt0111161",
    "tmdbId": "movie/278",
    "title": "The Shawshank Redemption",
    "originalTitle": "The Shawshank Redemption",
    "overview": "Two imprisoned men bond over a number of years.",
    "releaseYear": 1994,
    "genres": [{"id": "drama", "name": "Drama"}],
    "directors": ["Frank Darabont"],
    "cast": ["Tim Robbins", "Morgan Freeman"],
    "rating": 91,
    "imageSet": {"verticalPoster": {"w240": "https://example.com/poster.jpg"}},
    "streamingOptions": {
        "us": [
            {
                "service": {"id": "netflix", "name": "Netflix"},
                "type": "subscription",
                "link": "https://netflix.com/watch/123",
                "audios": [{"language": "en"}],
                "subtitles": [{"locale": {"language": "en"}, "closedCaptions": True}],
                "expiresSoon": False,
                "availableSince": 1600000000,
            }
        ]
    },
}

SAMPLE_SEARCH_RESULT = {
    "shows": [SAMPLE_SHOW],
    "hasMore": True,
    "nextCursor": "abc123",
}

SAMPLE_COUNTRIES = {
    "us": {
        "countryCode": "us",
        "name": "United States",
        "services": [
            {
                "id": "netflix",
                "name": "Netflix",
                "homePage": "https://netflix.com",
                "themeColorCode": "#E50914",
                "streamingOptionTypes": {
                    "subscription": True,
                    "free": False,
                    "rent": False,
                    "buy": False,
                    "addon": False,
                },
            }
        ],
    }
}

SAMPLE_COUNTRY = SAMPLE_COUNTRIES["us"]

SAMPLE_GENRES = {
    "action": {"id": "action", "name": "Action"},
    "drama": {"id": "drama", "name": "Drama"},
}

SAMPLE_CHANGES_RESULT = {
    "changes": [
        {
            "changeType": "new",
            "itemType": "show",
            "showId": "tt0111161",
            "timestamp": 1700000000,
        }
    ],
    "shows": {"tt0111161": SAMPLE_SHOW},
    "hasMore": False,
}

ERROR_NOT_FOUND = {"message": "Show not found"}
ERROR_GENERIC = {"message": "Something went wrong"}
