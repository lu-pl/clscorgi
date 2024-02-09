"""ELTeC runner: Main entry point for ELTeC conversions."""

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
    uris: Iterator[str] = get_eltec_xml_links(repos=[repo])

    _output_path = files("clscorgi.output.eltec")
    _output_file_name: str = f'{repo.lower().replace("-", "_")}.ttl'
    output_file: Path = _output_path / _output_file_name  # type: ignore

    g = Graph()
    CLSInfraNamespaceManager(g)

    for uri in uris:
        bindings = ELTeCBindingsExtractor(uri)
        print(bindings)
        triples = ELTeCRDFGenerator(**bindings)

        logger.info(f"Generating triples for {Path(uri).stem}")

        for triple in triples:
            g.add(triple)

    with open(output_file, "w") as f:
        f.write(g.serialize())

def eltec_runner() -> None:
    """ELTeC runner."""
    for repo in _REPOS:
        _generate_graph(repo)
