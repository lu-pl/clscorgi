"""ELTeC runner: Main entry point for ELTeC conversions."""

import json

from collections.abc import Iterator
from os import PathLike
from pathlib import Path

from importlib.resources import files

from clisn import CLSInfraNamespaceManager
from lodkit.graph import Graph
from loguru import logger

from clscorgi.eltec.extractors.bindings_extractor import ELTeCBindingsExtractor
from clscorgi.eltec.extractors.link_extractor import get_eltec_xml_links
from clscorgi.rdfgenerators import ELTeCRDFGenerator


_REPOS: list[str] = [
    "ELTeC-eng",
    "ELTeC-deu",
    "ELTeC-cze",
    "ELTeC-fra",
    "ELTeC-spa",
]

def _generate_graph(repo: str) -> None:
    """Process an ELTeC repo, generate a graph and serialize to output files."""

    _input_file = files("clscorgi.eltec.data.generated") / "eltec.json"
    output_file = files("clscorgi.output.eltec") / "from_json.ttl"

    with open(_input_file) as input_f:
        input_json = json.load(input_f)

    g = Graph()
    CLSInfraNamespaceManager(g)

    for data in input_json:
        triples = ELTeCRDFGenerator(**data)

        for triple in triples:
            g.add(triple)

    with open(output_file, "w") as f:
        f.write(g.serialize())

def eltec_runner() -> None:
    """ELTeC runner."""
    for repo in _REPOS:
        _generate_graph(repo)
