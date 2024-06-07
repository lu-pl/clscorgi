"""Functionality for extracting CLSCor triples from Postdata graphs."""

from collections.abc import Iterator

from lodkit import _Triple
from rdflib import BNode, Graph, Literal, Namespace, URIRef

_post_data_namespace_uris: list[str] = [
    "http://postdata.linhd.uned.es/resource/",
    "http://postdata.linhd.uned.es/ontology/postdata-core#",
    "http://postdata.linhd.uned.es/ontology/postdata-poeticAnalysis#",
    "http://postdata.linhd.uned.es/kos/"
]

postdata_namespaces: list[Namespace] = [
    Namespace(uri)
    for uri in _post_data_namespace_uris
]


def _clscor_relevant_component_p(component: URIRef | Literal | BNode) -> bool:
    match component:
        case Literal():
            return True
        case URIRef():
            return not any((component in ns) for ns in postdata_namespaces)
        case _:
            raise Exception("This should never happen.")


def _clscor_relevant_triple_p(triple: _Triple) -> bool:
    return all(
        _clscor_relevant_component_p(component)
        for component in triple
    )


def get_clscor_relevant_triples_from_graph(graph: Graph) -> Iterator[_Triple]:
    """Extract CLSCor triples from a Graph object."""
    for triple in graph.triples((None, None, None)):
        if _clscor_relevant_triple_p(triple):
            yield triple
