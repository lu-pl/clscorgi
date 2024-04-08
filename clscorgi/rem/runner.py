"""ReM runner: Main entry point for ReM conversions."""

import json

from collections.abc import Iterator
from itertools import chain
from importlib.resources import files

from rdflib import Graph
from clisn import CLSInfraNamespaceManager
from lodkit import _Triple

from clscorgi.rdfgenerators import ReMRDFGenerator
from clscorgi.rem.triple_generators import e55_triples


def _generate_triples() -> Iterator[_Triple]:
    data_file = files("clscorgi.rem.data.generated") / "rem.json"

    with open(data_file) as f:
        data = json.load(f)

    main_triples: Iterator[_Triple] = chain.from_iterable(
        ReMRDFGenerator(**bindings)
        for bindings in data
    )

    triples = chain(main_triples, e55_triples())
    return triples


def rem_runner() -> None:
    output_file = files("clscorgi.output.rem") / "rem.ttl"
    triples = _generate_triples()

    graph = Graph()
    CLSInfraNamespaceManager(graph)

    for triple in triples:
        graph.add(triple)

    with open(output_file, "w") as f:
        f.write(graph.serialize())
