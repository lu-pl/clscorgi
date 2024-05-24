"""Persist DLK data as JSON for further processing."""

import json

from collections.abc import Iterator
from importlib.resources import files

from clscorgi.dlk.extractors.link_extractor import get_dlk_raw_links
from clscorgi.dlk.extractors.bindings_extractor import DLKBindingsExtractor
from clscorgi.models import DLKBindingsModel


def get_dlk_data() -> Iterator[dict]:
    """Generate dlk data."""
    dlk_uris = get_dlk_raw_links()

    for dlk_uri in dlk_uris:
        print(dlk_uri)
        dlk_bindings = DLKBindingsExtractor(dlk_uri)
        yield dict(dlk_bindings)


if __name__ == "__main__":
    data_file = files("clscorgi.dlk.data.generated") / "dlk.json"
    data = list(get_dlk_data())

    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)
