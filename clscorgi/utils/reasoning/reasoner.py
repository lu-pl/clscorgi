"""OWL RL Reasoner for CLSCorgi"""

from collections.abc import Iterator
import os
from pathlib import Path
from typing import Iterable

from owlrl import CombinedClosure, DeductiveClosure
from rdflib import Graph


def _get_ontology_graph(ontologies: Iterable[os.PathLike]) -> Graph:
    graph = Graph()

    for ontology in ontologies:
        ontology_graph = Graph().parse(ontology)
        graph += ontology_graph

    return graph


def _get_ontology_paths() -> Iterator[Path]:
    for path in Path("./ontologies").iterdir():
        if path.suffix in [".rdf", ".ttl"]:
            yield path


def run_reasoner(graph: Graph) -> Graph:
    """Run a reasoner with RDFS + OWLRL closure on graph."""
    closure = DeductiveClosure(
        CombinedClosure.RDFS_OWLRL_Semantics,
    )
    ontology_graph = _get_ontology_graph(_get_ontology_paths())
    combined_graph = graph + ontology_graph

    closure.expand(combined_graph)
    return combined_graph
