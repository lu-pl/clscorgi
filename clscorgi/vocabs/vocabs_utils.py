"""General utilities concerning vocabs."""

from collections.abc import Iterable
from importlib.resources import files
from pathlib import Path
from urllib.parse import urlparse

import httpx


def _pull_remote_vocab(vocab_url: str) -> None:
    vocabs_path = files("clscorgi.vocabs")
    file_name = Path(urlparse(vocab_url).path).name
    response = httpx.get(vocab_url)

    with open(str(vocabs_path / file_name), "wb") as f:
        f.write(response.content)


def _pull_remote_vocabs(vocab_urls: Iterable[str]):
    for url in vocab_urls:
        _pull_remote_vocab(url)


vocab_urls = [
    "https://gitlab.clsinfra.io/cls-infra/wp567/clscor/-/raw/main/vocabs/appellation_vocab/appellation.ttl",
    "https://gitlab.clsinfra.io/cls-infra/wp567/clscor/-/raw/main/vocabs/method_vocab/method.ttl",
]


def pull_remote_vocabs():
    """Pull all remote vocabs specified in vocab_urls."""
    _pull_remote_vocabs(vocab_urls)
