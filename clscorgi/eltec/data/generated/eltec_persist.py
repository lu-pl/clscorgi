"""Persist ELTeC data as JSON for further prossing."""

import json
from collections.abc import Iterator
from importlib.resources import files

from clscorgi.eltec.extractors.bindings_extractor import ELTeCBindingsExtractor
from clscorgi.eltec.extractors.link_extractor import get_eltec_xml_links

_REPOS: list[str] = [
    "ELTeC-eng",
    "ELTeC-deu",
    "ELTeC-cze",
    "ELTeC-fra",
    "ELTeC-spa",
]

if __name__ == "__main__":
    for repo in _REPOS:
        uris: Iterator[str] = get_eltec_xml_links(repos=[repo])
        data_file = files("clscorgi.eltec.data.generated") / f"{repo.lower()}.json"

        bindings = [
            dict(ELTeCBindingsExtractor(uri))
            for uri in uris
        ]

        with open(data_file, "w") as f:
            json.dump(bindings, f, indent=4)
