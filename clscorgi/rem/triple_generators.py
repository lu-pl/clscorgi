"""Triple generators for ReM conversions."""

import itertools

from collections.abc import Iterator

from clisn import crmcls, lrm, crm
from lodkit import mkuri_factory, URINamespace, ttl, _Triple

from rdflib import Literal, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, XSD

from clscorgi.models import ReMBindingsModel
from clscorgi.utils.utils import require_defaults


e55_pairs: tuple[tuple[str, str]] = (
    ("e55_work_title", "ReM Work Title [Type]"),
    ("e55_rem_document_id", "ReM Document ID [Type]"),
    ("e55_genre_assignment", "ReM Genre Assignment [Type]"),
    ("e55_genre", "ReM Genre [Type]")
)

mkuri = mkuri_factory(crmcls)
uris = URINamespace(
    namespace=crmcls,
    names=(
        "f1", "f2", "x2", "f3pub", "f3src", "f5",
        "f27", "f28", "e35", "e17",
        ("x1_rem", "ReM [X1]"),
        ("x11_rem", "ReM [X11]"),
        *e55_pairs
    )
)

def f1_triple_generator(bindings: ReMBindingsModel) -> Iterator[_Triple]:
    f1_triples = ttl(
        uris.f1,
        (RDF.type, lrm.F1_Work),
        (RDFS.label, Literal(f"{bindings.title} [Work]")),
        (lrm.R3_is_realised_in, uris.f2),
        (lrm.R16i_was_created_by, uris.f27)
    )

    return f1_triples


def f2_triple_generator(bindings: ReMBindingsModel) -> Iterator[_Triple]:
    f2_triples = ttl(
        uris.f2,
        (RDF.type, lrm.F2_Expression),
        (RDFS.label, Literal(f"{bindings.title} [Expression]")),
        (lrm.R3i_realises, uris.f1),
        (lrm.R4i_is_embodied_in, (uris.f3pub, uris.f3src)),
        (lrm.R17i_was_created_by, uris.f28)
    )

    return f2_triples


def x2_triple_generator(bindings: ReMBindingsModel) -> Iterator[_Triple]:
    x2_triples = ttl(
        uris.x2,
        (RDF.type, crmcls.X2_Corpus_Document),
        (RDFS.label, Literal(f"{bindings.title} [Corpus Document Manifestation]")),
        (lrm.R4_embodies, uris.f2),
        (crm.P1_is_identified_by, ttl(
            mkuri(),
            (RDF.type, crm.E42_Identifier),
            (RDFS.label, Literal(f"{bindings.title} [ReM ID]")),
            (crm.P190_has_symbolic_value, Literal(f"{bindings.id}")),
            (crm.P2_has_type, uris.e55_rem_document_id)
        )),
        (lrm.R71i_is_part_of, ttl(uris.x1_rem, (RDF.type, crmcls.X1_Corpus))),
        (crm.P137_exemplifies, ttl(uris.x11_rem, (RDF.type, crmcls.X11_Prototypical_Document))),
        (crmcls.Y2_has_format, URIRef("https://clscor.io/entity/type/format/tei")),
        (crmcls.Y1_exhibits_feature, [
            (RDF.type, crmcls.X3_Feature),
            (crm.P2_has_type, URIRef("https://clscor.io/entity/type/feature/token")),
            (crm.P91i_is_unit_of, [
                (RDF.type, crm.E54_Dimension),
                (crm.P90_has_value, Literal(f"{bindings.token_count}", datatype=XSD.integer))
            ])
        ])

        )

    return x2_triples


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


def f3_triple_generator(bindings: ReMBindingsModel) -> Iterator[_Triple]:
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

    return itertools.chain(f3pub_triples, f3src_triples)


def _f5_e42_generator(symbolic_content: str | None):
    if symbolic_content:
        return ttl(
            uris.f5,
            (crm.P1_is_identified_by, [
             (RDF.type, crm.E42_Identifier),
             (crm.P190_has_symbolic_content, Literal(symbolic_content))
            ])
        )
    return ()


def f5_triple_generator(bindings: ReMBindingsModel) -> Iterator[_Triple]:
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

    e42_msname = _f5_e42_generator(bindings.source.msname)
    e42_census = _f5_e42_generator(bindings.source.census_link)

    return itertools.chain(f5_base_triples, e42_msname, e42_census)


def e35_triple_generator(bindings: ReMBindingsModel) -> Iterator[_Triple]:
    return ttl(
        uris.e35,
        (RDF.type, crm.E35_Title),
        (RDFS.label, Literal(f"{bindings.title} [Title]")),
        (crm.P190_has_symbolic_content, Literal(f"{bindings.title} [Title]")),
        (crm.P102i_is_title_of, (uris.f1, uris.f2, uris.x2)),
        (crm.P2_has_type, uris.e55_work_title),
    )

def e17_triple_generator(bindings: ReMBindingsModel) -> Iterator[_Triple]:
    genre: str = bindings.genre or "Undefined"

    e17_triples = ttl(
        uris.e17,
        (RDF.type, crm.E17_Type_Assignment),
        (crm.P2_has_type, uris.e55_genre_assignment),
        (crm.P41_classified, (uris.f1, uris.f2, uris.x2, uris.f3pub, uris.f3src)),
        (crm.P42_assigned, ttl(
            mkuri(f"{genre} [ReM Genre]"),
            (RDF.type, crm.E55_type),
            (crm.P2_has_type, uris.e55_genre),
            (RDFS.label, Literal(f"{genre} [ReM Genre]"))
        ))
    )

    return e17_triples



# note: to avoid generation for every binding set, this should be preloaded in the aggregate graph
def e55_triples() -> Iterator[_Triple]:
    for name, label in e55_pairs:
        uri = getattr(uris, name)
        yield from ttl(
            uri,
            (RDF.type, crm.E55_Type),
            (RDFS.label, Literal(label))
        )

    yield (
        uris.e55_genre,
        crm.P1_is_identified,
        URIRef("https://www.wikidata.org/entity/Q483394")
    )
