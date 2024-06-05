"""Triple generators for the Gutenberg Corpus."""

from collections.abc import Iterator
from itertools import chain

from clisn import clscore, crm, crmcls, lrm
from clscorgi.models import GutenbergBindingsModel
from lodkit import URINamespace, _Triple, mkuri_factory, ttl
from rdflib import Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

mkuri = mkuri_factory(clscore)


def lrm_boilerplate_triple_generator(
        bindings: GutenbergBindingsModel,
        namespace: URINamespace
) -> Iterator[_Triple]:
    """Triple generator for LRM boilerplate.."""
    _author_uris = {
        author_name: mkuri(author_name)
        for author_name
        in [author.name for author in bindings.authors]
    }

    f1_triples = ttl(
        namespace.f1,
        (RDF.type, lrm.F1_Work),
        (RDFS.label, Literal(f"{bindings.title} [Work Title]")),
        (lrm.R3_is_realized_in, namespace.f2),
        # inverse
        (lrm.R16i_was_created_by, namespace.f27)
    )

    f2_triples = ttl(
        namespace.f2,
        (RDF.type, lrm.F2_Expression),
        (RDFS.label, Literal(f"{bindings.title} [Expression Title]")),
        (lrm.R4i_is_embodied_in, namespace.x2),
        # inverse
        (lrm.R17i_was_created_by, namespace.f28)
    )

    f27_triples = ttl(
        namespace.f27,
        (RDF.type, lrm.F27_Work_Creation),
        (lrm.R16_created, namespace.f1),
        (crm.P14_carried_out_by, tuple(_author_uris.values()))
    )

    f28_triples = ttl(
        namespace.f28,
        (RDF.type, lrm.F28_Expression_Creation),
        (lrm.R17_created, namespace.f2),
        (crm.P14_carried_out_by, tuple(_author_uris.values()))
    )

    def author_triples() -> Iterator[_Triple]:
        for author_name, author_uri in _author_uris.items():
            yield from ttl(
                author_uri,
                (RDF.type, crm.E39_Actor),
                (RDFS.label, Literal(f"{author_name} [Actor]")),
                (crm.P1_is_identified_by, ttl(
                    mkuri(f"{author_name} [Actor Appellation]"),
                    (RDF.type, crm.E41_Appellation),
                    (crm.P190_has_symbolic_content, Literal(f"{author_name} [Actor]"))
                )),
                # inverses
                (crm.P14i_performed, (namespace.f27, namespace.f28))
            )

    triples = chain(
        f1_triples,
        f2_triples,
        f27_triples,
        f28_triples,
        author_triples()
    )

    return triples


def x2_pg_triple_generator(
        bindings: GutenbergBindingsModel,
        namespace: URINamespace
) -> Iterator[_Triple]:
    """Triple generator for X2 assertions."""
    main_x2_triples =  ttl(
        namespace.x2,
        (RDF.type, crmcls.X2_Corpus_Document),
        (RDFS.label, Literal(f"{bindings.title} [Corpus Document Title]")),
        (RDFS.seeAlso, URIRef(bindings.formats["application/rdf+xml"])),
        (lrm.R4_embodies, namespace.f2),
        (lrm.R71i_is_part_of, namespace.x1_gutenberg),
        (crm.P148i_is_component_of, ttl(
            namespace.x1_gutenberg,
            (crm.P148_has_component, namespace.x2),
            (lrm.R71_has_part, namespace.x2)
        )),
        (crm.P137_exemplifies, namespace.x11_gutenberg),
        (crm.P72_has_language, tuple(
            Namespace("https://vocabs.acdh.oeaw.ac.at/iso6391/")[lang]
            for lang in bindings.languages
        )),
        (crm.P1_is_identified_by, [
            (RDF.type, crm.E42_Identifier),
            (RDFS.label, Literal(f"{bindings.title} [Gutenberg ID]")),
            (crm.P190_has_symbolic_value, Literal(f"{bindings.id}", datatype=XSD.integer)),
            (crm.P2_has_type, namespace.e55_id)
        ]),
        (crm.P1_is_identified_by, [
            (RDF.type, crm.E42_Identifier),
            (RDFS.label, Literal(f"{bindings.title} [Gutenberg ID URL]")),
            (crm.P190_has_symbolic_value, Literal(f"{bindings.id_url}", datatype=XSD.anyURI)),
            (crm.P2_has_type, namespace.e55_id_url)
        ])
    )

    def e36_triples() -> Iterator[_Triple]:
        try:
            image_uri = bindings.formats["image/jpeg"]
        except KeyError:
            # equal to "StopIteration"
            return
        else:
            yield from ttl(
                namespace.x2,
                (crm.P148_has_component, [
                    (RDF.type, crm.E36_Visual_Item),
                    (RDFS.label, Literal(f"{bindings.title} [Visual Item]")),
                    (crm.P138_represents, namespace.x2),
                    (crm.P1_is_identified_by, [
                        (RDF.type, crm.E42_Identifier),
                        (crm.P190_has_symbolic_content, Literal(image_uri))
                    ])
                ]))

    return chain(
        main_x2_triples,
        e36_triples()
    )

def e55_triple_generator() -> Iterator[_Triple]:
    """Static E55 triple generators."""
    e55_id_triples = ttl(
        mkuri("Gutenberg ID [Type]"),
        (RDF.type, crm.E55_Type),
        (RDFS.label, Literal("Gutenberg Document ID"))

    )

    e55_id_url_triples = ttl(
        mkuri("Gutenberg ID URL [Type]"),
        (RDF.type, crm.E55_Type),
        (RDFS.label, Literal("Gutenberg Document ID URL"))
    )

    return chain(
        e55_id_triples,
        e55_id_url_triples
    )
