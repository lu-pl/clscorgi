"""Generic Vocab Lookup Utility. This is intended to supersed the clscorgi.vocabs.vocabs solution."""

from collections.abc import Callable
from functools import partial
from importlib.resources import files
import os

from rdflib import Graph, Literal, RDFS, URIRef


class VocabLookupException(Exception):
    """Exception for indicating a failed vocab term lookup."""


class Vocabs:
    """Vocabs Lookup Utility.

    The class allows to reverse-lookup subject URIs based on an rdfs:label term
    for several graphs which can be accessed by the vocabs name.

    Example:

    vocabs = Vocabs(identifier=_vocabs_path / "identifier.ttl")
    print(vocabs.identifier("textgrid"))  # https://clscor.io/entity/type/identifier/textgrid
    """

    def __init__(self, **vocabs: os.PathLike | Graph) -> None:
        self._vocabs = vocabs

        self._vocab_graphs: list[Graph] = [
            graph if isinstance(graph, Graph) else Graph().parse(graph)
            for _, graph in self._vocabs.items()
        ]
        self._lookup_map: dict[str, Callable[[str], URIRef]] = {
            name: partial(self._lookup_term, graph=graph)
            for name, graph in zip(self._vocabs.keys(), self._vocab_graphs)
        }

    def __getattr__(self, attr) -> URIRef:
        return self._lookup_map[attr]

    def _lookup_term(self, term: str, graph: Graph) -> URIRef:
        """Lookup a subject URI in a Graph based on its rdfs:label term."""
        _subjects = graph.subjects(RDFS.label, Literal(term))

        try:
            vocab_uri = next(_subjects)
        except StopIteration:
            raise VocabLookupException(f"No subject URI for term '{term}'.")

        return vocab_uri


_vocabs_path = files("clscorgi.vocabs")
_vocabs_files = [f for f in _vocabs_path.iterdir() if f.suffix == ".ttl"]

vocabs_id_path_map: dict = {
    f.stem: f for f in _vocabs_path.iterdir() if f.suffix == ".ttl"
}

vocabs = Vocabs(**vocabs_id_path_map)
