"""Gutenberg runner: Main entry point for Gutenberg conversions."""

import itertools
from itertools import count
from importlib.resources import files

from rdflib import Graph
from clisn import CLSInfraNamespaceManager

from clscorgi.gutenberg.extractor import get_gutendex_sliced_chunks
from clscorgi.gutenberg.triple_generators import e55_triple_generator
from clscorgi.rdfgenerators import GutenbergRDFGenerator


def gutenberg_runner() -> None:
    "Runner for Gutenberg RDF conversion."
    cnt = count()
    output_dir = files("clscorgi.output.gutenberg")

    for data in get_gutendex_sliced_chunks():
        output_file = output_dir / f"gutenberg_{next(cnt)}.ttl"

        main_triples = itertools.chain.from_iterable(
            GutenbergRDFGenerator(**bindings)
            for bindings in data
        )

        triples = itertools.chain(
            main_triples,
            e55_triple_generator()
        )

        graph = Graph()
        CLSInfraNamespaceManager(graph)

        for triple in triples:
            graph.add(triple)

        with open(output_file, "w") as f:
            f.write(graph.serialize())
