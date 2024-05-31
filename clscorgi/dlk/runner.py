"""DLK runner: Main entry point for DLK RDF conversions."""

import itertools
import json
from collections.abc import Iterator
from importlib.resources import files

from clisn import CLSInfraNamespaceManager
from clscorgi.rdfgenerators import DLKRDFGenerator
from lodkit import _Triple
from rdflib import Graph


def _generate_triples() -> Iterator[_Triple]:
    data_file = files("clscorgi.dlk.data.generated") / "dlk.json"

    with open(data_file) as f:
        data = json.load(f)

    triples = itertools.chain.from_iterable(
        DLKRDFGenerator(**bindings)
        for bindings in data
    )

    return triples



def dlk_runner() -> None:
    """Runner for DLK RDF conversions."""
    output_file = files("clscorgi.output.dlk") / "dlk.ttl"

    graph = Graph()
    CLSInfraNamespaceManager(graph)

    triples = _generate_triples()

    for triple in triples:
        graph.add(triple)

    with open(output_file, "w") as f:
        f.write(graph.serialize())
