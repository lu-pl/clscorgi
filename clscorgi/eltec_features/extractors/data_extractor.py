"""Data extraction generator for ELTeC features."""

import json
from collections.abc import Iterable, Iterator
from urllib.request import urlretrieve

_REPOS: list[str] = [
    "ELTeC-eng",
    "ELTeC-deu",
    "ELTeC-cze",
    "ELTeC-fra",
    "ELTeC-spa",
]


def _get_eltec_features_links(repos: Iterable[str] = _REPOS) -> Iterator[str]:
    """Construct a raw link for an ELTeC feature analysis."""
    _template = (
        "https://raw.githubusercontent.com/acdh-oeaw/"
        "veld_data_16_eltec_conllu_stats/main/data/{}.json"
    )

    for repo in repos:
        yield _template.format(repo)


def get_eltec_features_data(links: Iterable[str] | None = None) -> Iterator[dict]:
    """Retrieve data from a remote ELTeC features repo."""
    _links = _get_eltec_features_links() if links is None else links
    for link in _links:
        _temp_file, _ = urlretrieve(link)
        with open(_temp_file) as f:
            feature_data = json.load(f)
            yield from feature_data
