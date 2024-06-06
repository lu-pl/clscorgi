"""Triple generators for ELTeC features."""

from clisn import clscore, crm, crmcls
from clscorgi.models import ELTeCFeaturesBindingsModel
from lodkit import URINamespace, mkuri_factory, ttl
from rdflib.namespace import RDF

mkuri = mkuri_factory(clscore)

def e13_eltec_features_generator(
        bindings: ELTeCFeaturesBindingsModel,
):
    """Triple generator for ELTec Features triples"""
    # mkuri(bindings.resource_uri)

    return ttl(
        mkuri(),
        (RDF.type, crm.E13_Attribute_Assignment)
    )
