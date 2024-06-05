"""Triple generators for ReM conversions."""

import itertools
from collections.abc import Iterator
from typing import NoReturn

from clisn import clscore, crm, crmcls, lrm
from clscorgi.models import ReMBindingsModel
from clscorgi.utils.utils import require_defaults
from lodkit import URINamespace, _Triple, mkuri_factory, ttl
from rdflib import Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

e55_pairs: tuple[tuple[str, str]] = (
    ("e55_work_title", "ReM Work Title [Type]"),
    ("e55_rem_document_id", "ReM Document ID [Type]"),
    ("e55_genre_assignment", "ReM Genre Assignment [Type]"),
    ("e55_genre", "Wikidata Genre [Type]"),
    ("e55_url_id", "ReM URL ID")
)

mkuri = mkuri_factory(crmcls)


def generate_uri_namespace() -> URINamespace:
    uris = URINamespace(
        namespace=clscore,
        names=(
            "f1", "f2", "x2", "f3pub", "f3src", "f5",
            "f27", "f28", "f30_x2", "f30_f3pub", "f30_f3src", "f32",
            "e17", "e35", "e52",
            ("x1_rem", "ReM [X1]"),
            ("x11_rem", "ReM [X11]"),
            *e55_pairs
        )
    )
    return uris


def f1_triple_generator(
        bindings: ReMBindingsModel,
        uris: URINamespace
) -> Iterator[_Triple]:
    f1_triples = ttl(
        uris.f1,
        (RDF.type, lrm.F1_Work),
        (RDFS.label, Literal(f"{bindings.title} [Work]")),
        (lrm.R3_is_realised_in, uris.f2),
        (lrm.R16i_was_created_by, uris.f27)
    )

    return f1_triples


def f2_triple_generator(
        bindings: ReMBindingsModel,
        uris: URINamespace
) -> Iterator[_Triple]:
    f2_triples = ttl(
        uris.f2,
        (RDF.type, lrm.F2_Expression),
        (RDFS.label, Literal(f"{bindings.title} [Expression]")),
        (lrm.R3i_realises, uris.f1),
        (lrm.R4i_is_embodied_in, (uris.f3pub, uris.f3src)),
        (lrm.R17i_was_created_by, uris.f28)
    )

    return f2_triples


def x2_triple_generator(
        bindings: ReMBindingsModel,
        uris: URINamespace
) -> Iterator[_Triple]:
    x2_triples = ttl(
        uris.x2,
        (RDF.type, crmcls.X2_Corpus_Document),
        (RDFS.label, Literal(f"{bindings.title} [Corpus Document Manifestation]")),
        (lrm.R4_embodies, uris.f2),
        (crm.P1_is_identified_by, ttl(
            mkuri(),
            (RDF.type, crm.E42_Identifier),
            (RDFS.label, Literal(f"{bindings.title} [ReM ID]")),
            (crm.P190_has_symbolic_content, Literal(f"{bindings.id}")),
            (crm.P2_has_type, uris.e55_rem_document_id)
        )),
        (crm.P1_is_identified_by, ttl(
            mkuri(),
            (RDF.type, crm.E42_Identifier),
            (RDFS.label, Literal(f"{bindings.title} [ReM URL ID]")),
            (crm.P190_has_symbolic_content, Literal(f"{bindings.resource_url}")),
            (crm.P2_has_type, uris.e55_url_id)
        )),
        (lrm.R71i_is_part_of, ttl(
            uris.x1_rem,
            (RDF.type, crmcls.X1_Corpus),
            (lrm.R71_has_part, uris.x2),
            (crm.P148_has_component, uris.x2)
        )),
        (crm.P137_exemplifies, ttl(uris.x11_rem, (RDF.type, crmcls.X11_Prototypical_Document))),
        (crmcls.Y2_has_format, URIRef("https://clscor.io/entity/type/format/tei"))
    )

    e13_feature_triples = ttl(
        mkuri(),
        (RDF.type, crm.E13_Attribute_Assignment),
        (crm.P16_used_specific_object, uris.x2),
        (crm.P140_assigned_attribute_to, uris.x2),
        (crm.P177_assigned_property_of_type, crmcls.Y1_exhibits_feature),
        (crm.P141_assigned, ttl(
            mkuri(),
            (RDF.type, crmcls.X3_Feature),
            (crm.P2_has_type, URIRef("https://clscor.io/entity/type/feature/token")),
            (crm.P91i_is_unit_of, [
                (RDF.type, crm.E54_Dimension),
                (crm.P90_has_value, Literal(f"{bindings.token_count}", datatype=XSD.integer))
            ])
        ))
    )

    triples = itertools.chain(
        x2_triples,
        e13_feature_triples
    )

    return triples


def f3_triple_generator(
        bindings: ReMBindingsModel,
        uris: URINamespace
) -> Iterator[_Triple]:
    def _f3_triple_template(
            uri: Namespace,
            label: str,
            symbolic_content: str | None
    ) -> Iterator[_Triple]:
        f3_base_triples = ttl(
            uri,
            (RDF.type, lrm.F3_Manifestation),
            (RDFS.label, Literal(label)),
            (lrm.R4_embodies, uris.f2))

        @require_defaults()
        def idno_triples(idno=symbolic_content):
            return ttl(
                uri,
                (crm.P1_is_identified_by, [
                    (RDF.type, crm.E41_Appellation),
                    (crm.P190_has_symbolic_content, Literal(f"{idno}"))
                ])
            )

        triples = itertools.chain(f3_base_triples, idno_triples())
        return triples


    f3pub_triples = _f3_triple_template(
        uri=uris.f3pub,
        label=f"{bindings.title} [Publication Manifestation]",
        symbolic_content=bindings.publication.idno
    )

    f3src_triples = _f3_triple_template(
        uri=uris.f3src,
        label=f"{bindings.title} [Source Manifestation]",
        symbolic_content=bindings.source.idno
    )

    return itertools.chain(
        f3pub_triples,
        f3src_triples
    )


def f5_triple_generator(
        bindings: ReMBindingsModel,
        uris: URINamespace
) -> Iterator[_Triple]:
    f5_base_triples = ttl(
        uris.f5,
        (RDF.type, lrm.F5_Item),
        (RDFS.label, Literal(f"{bindings.title} [Physical Item]")),
        (lrm.R7_exemplifies, uris.f3src),
        (crm.P49_has_former_or_current_keeper, [
            (RDF.type, lrm.F11_Corporate_Body),
            (RDFS.label, Literal(bindings.source.repo)),
            (crm.P1_is_identified_by, [
                (RDF.type, crm.E41_Appellation),
                (crm.P190_has_symbolic_content, Literal(bindings.source.repo))
            ])
        ])
    )

    def _f5_e42_generator(symbolic_content: str | None):
        if symbolic_content:
            yield from ttl(
                uris.f5,
                (crm.P1_is_identified_by, [
                    (RDF.type, crm.E42_Identifier),
                    (crm.P190_has_symbolic_content, Literal(symbolic_content))
                ])
            )

        # return from a generator is equivalent to raise StopIteration
        # https://stackoverflow.com/a/16780113/6455731
        return

    e42_msname = _f5_e42_generator(bindings.source.msname)
    e42_census = _f5_e42_generator(bindings.source.census_link)

    return itertools.chain(f5_base_triples, e42_msname, e42_census)


def e17_triple_generator(
        bindings: ReMBindingsModel,
        uris: URINamespace
) -> Iterator[_Triple]:
    genre: str = bindings.genre or "Undefined"

    e17_triples = ttl(
        uris.e17,
        (RDF.type, crm.E17_Type_Assignment),
        (crm.P2_has_type, uris.e55_genre_assignment),
        (crm.P41_classified, (uris.f1, uris.f2, uris.x2, uris.f3pub, uris.f3src)),
        (crm.P42_assigned, ttl(
            mkuri(f"{genre} [ReM Genre]"),
            (RDF.type, crm.E55_Type),
            (RDFS.label, Literal(f"{genre} [ReM Genre]")),
            (crm.P127_has_broader_term, uris.e55_genre)
        ))
    )

    return e17_triples


def e35_triple_generator(
        bindings: ReMBindingsModel,
        uris: URINamespace
) -> Iterator[_Triple]:
    return ttl(
        uris.e35,
        (RDF.type, crm.E35_Title),
        (RDFS.label, Literal(f"{bindings.title} [Title]")),
        (crm.P190_has_symbolic_content, Literal(f"{bindings.title} [Title]")),
        (crm.P102i_is_title_of, (uris.f1, uris.f2, uris.x2)),
        (crm.P2_has_type, uris.e55_work_title),
    )

def wemi_e2_triple_generator(
        bindings: ReMBindingsModel,
        uris: URINamespace
) -> Iterator[_Triple]:
    f27_triples = ttl(
        uris.f27,
        (RDF.type, lrm.F27_Work_Creation),
        (RDFS.label, Literal(f"{bindings.title} [Work Creation]")),
        (lrm.R16_created, uris.f1)
    )

    f28_triples = ttl(
        uris.f28,
        (RDF.type, lrm.F28_Expression_Creation),
        (RDFS.label, Literal(f"{bindings.title} [Expression Creation]")),
        (lrm.R19_created_a_realisation_of, uris.f1),
        (lrm.R17_created, uris.f2)
    )

    f30_x2_triples = ttl(
        uris.f30_x2,
        (RDF.type, lrm.F30_Manifestation_Creation),
        (RDFS.label, Literal(f"{bindings.title} [Manifestation Creation]")),
        (lrm.R24_created, uris.x2)
    )

    f30_f3src_triples = ttl(
        uris.f30_f3src,
        (RDF.type, lrm.F30_Manifestation_Creation),
        (RDFS.label, Literal(f"{bindings.source.idno} [Manifestation Creation]")),
        (lrm.R24_created, uris.f3src)
    )

    def f30_f3pub_triples() -> Iterator[_Triple]:
        if pub_idno := bindings.publication.idno:
            yield from ttl(
                uris.f30_f3pub,
                (RDF.type, lrm.F30_Manifestation_Creation),
                (RDFS.label, Literal(f"{pub_idno} [Manifestation Creation]")),
                (lrm.R24_created, uris.f3pub)
            )

            if date := bindings.publication.date:
                yield from ttl(
                    uris.f30_f3pub,
                    (crm["P4_has_time-span"], [
                        (RDF.type, crm["E52_Time-Span"]),
                        (crm.P82_at_some_time_within, Literal(date, datatype=XSD.gYear))
                    ])
                )

        return

    def f32_triples() -> Iterator[_Triple]:
        yield from ttl(
            uris.f32,
            (RDF.type, lrm.F32_Item_Production_Event),
            (RDFS.label, Literal(f"{bindings.source.idno} [Item Production]")),
            (lrm.R26_produced, uris.f5),
            (lrm.R27_materialized, uris.f3src),
        )


        if bindings.source.tpq or bindings.source.taq:
            yield from ttl(
                uris.f32,
                (crm["P4_has_time-span"], ttl(
                    uris.e52, (RDF.type, crm["E52_Time-Span"])
                ))
            )

            if tpq := bindings.source.tpq:
                yield (uris.e52, crm.P81a_end_of_the_begin, Literal(tpq, datatype=XSD.gYear))
            if taq := bindings.source.taq:
                yield (uris.e52, crm.P81b_begin_of_the_end, Literal(taq, datatype=XSD.gYear))


    return itertools.chain(
        f27_triples,
        f28_triples,
        f30_x2_triples,
        f30_f3src_triples,
        f30_f3pub_triples(),
        f32_triples()
    )


def e55_triples() -> Iterator[_Triple]:
    """E55 triple generator.

    E55 triples are not intended to get generated from an RDFGenerator,
    but should be preloaded in the aggregate graph.
    """
    for _, label in e55_pairs:
        uri = mkuri(label)
        yield from ttl(
            uri,
            (RDF.type, crm.E55_Type),
            (RDFS.label, Literal(label))
        )

    yield (
        mkuri("Wikidata Genre [Type]"),
        crm.P1_is_identified,
        URIRef("https://www.wikidata.org/entity/Q483394")
    )
