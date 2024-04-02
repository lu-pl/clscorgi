"""Generators for retrieving Gutendex results."""

from collections.abc import Iterator
from itertools import islice

import requests
from more_itertools import ichunked


def get_gutendex_results(url: str = "https://gutendex.com/books/") -> Iterator[dict]:
    """Generator for retrieving ALL Gutendex results."""
    response = requests.get(url)
    json_response = response.json()

    yield from json_response["results"]

    if (next_page := json_response["next"]) is not None:
        yield from get_gutendex_results(url=next_page)


def get_gutendex_sliced_chunks(
        slice_size: int = 5,
        chunk_size: int = 100
) -> Iterator[Iterator[dict]]:
    """Get sliced chunks of Gutenberg datasets."""
    return islice(ichunked(get_gutendex_results(), chunk_size), slice_size)
