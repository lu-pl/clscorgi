"""Triple generators for ELTeC features."""

from clisn import clscore, crm, crmcls, crmdig
from clscorgi.models import ELTeCFeaturesBindingsModel
from lodkit import URINamespace, mkuri_factory, ttl
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, XSD

mkuri = mkuri_factory(clscore)

def e13_eltec_features_generator(
        bindings: ELTeCFeaturesBindingsModel,
):
    """Triple generator for ELTec Features triples"""
    x2_uri = mkuri(f"{bindings.resource_uri} [X2]")

    e13_token_triples = ttl(
        mkuri(),
        (RDF.type, crm.E13_Attribute_Assignment),
        (crm.P16_used_specific_object, ttl(
            mkuri("veld_data_16_eltec_conllu_stats [D1]"),
            (RDF.type, crmdig.D1_Digital_Object),
            (crm.P1_is_identified_by, ttl(
                mkuri("veld_data_16_eltec_conllu_stats [E42]"),
                (RDF.type, crm.E42_Identifier),
                (crm.P190_has_symbolic_content,
                 Literal("https://github.com/acdh-oeaw/veld_data_16_eltec_conllu_stats/"))
            ))
        )),
        (crm.P140_assigned_attribute_to, x2_uri),
        (crm.P177_assigned_property_of_type, crmcls.Y1_exhibits_feature),
        (crm.P141_assigned, ttl(
            mkuri(),
            (RDF.type, crmcls.X3_Feature),
            (crm.P2_has_type, URIRef("https://clscor.io/entity/type/feature/token")),
            (crm.P91i_is_unit_of, [
                (RDF.type, crm.E54_Dimension),
                (crm.P90_has_value,
                 Literal(f"{bindings.conllu_stats.count_token}", datatype=XSD.integer))
            ])
        )))

    return e13_token_triples
