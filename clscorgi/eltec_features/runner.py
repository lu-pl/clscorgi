"""Runner for ELTeC feature RDF generation."""

from importlib.resources import files

from clisn import CLSInfraNamespaceManager
from clscorgi.eltec_features.extractors.data_extractor import \
    get_eltec_features_data
from clscorgi.rdfgenerators import ELTeCFeaturesRDFGenerator
from rdflib import Graph


def _generate_eltec_feature_graph() -> Graph:
    """Generate a graph object from remote Conllu data."""
    feature_data = get_eltec_features_data()
    graph = Graph()
    CLSInfraNamespaceManager(graph)

    for bindings in feature_data:
        triples = ELTeCFeaturesRDFGenerator(**bindings)
        for triple in triples:
            graph.add(triple)

    return graph


def eltec_feature_runner() -> None:
    """ELTeC features runner."""
    output_file = files("clscorgi.output.eltec_features") / "eltec_features.ttl"
    graph = _generate_eltec_feature_graph()

    with open(output_file, "w") as f:
        f.write(graph.serialize())
