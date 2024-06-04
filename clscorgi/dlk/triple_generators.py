"""Triple generators for the DLK corpus."""

import itertools
from collections.abc import Iterator

from clisn import clscore, crm, lrm
from clscorgi.models import DLKBindingsModel
from lodkit import URINamespace, _Triple, mkuri_factory, ttl
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

mkuri = mkuri_factory(clscore)


class dlk_wemi_triples:
    """Triple generator for DLK wemi triples."""

    def __init__(
            self,
            bindings: DLKBindingsModel,
            namespace: URINamespace
    ) -> None: # noqa
        self.bindings = bindings
        self.namespace = namespace

        self.title = self.bindings.title or self.bindings.artificial_title
        self.authors_mapping: dict[str, URIRef] = {
            author.full_name: mkuri(author.full_name)
            for author in self.bindings.authors
        }
        self.triples: Iterator[_Triple] = itertools.chain(
            self.f123_triples(),
            self.e35_triples(),
            self.x2_triples(),
            self.lrm_e2_triples(),
            self.e39_triples()
        )

    def __next__(self) -> _Triple: # noqa
        return next(self.triples)

    def __iter__(self) -> Iterator[_Triple]: # noqa
        return self

    def e35_triples(self) -> Iterator[_Triple]:
        """Triple generator for E35s."""
        yield from ttl(
            mkuri(f"{self.title} [Title]"),
            (RDF.type, crm.E35_Title),
            (
                crm.P102i_is_title_of, (
                    self.namespace.f1,
                    self.namespace.f2,
                    self.namespace.f3,
                    self.namespace.x2,
                )
            )
        )

        if self.bindings.title is None:
            artificial_title = URIRef(
                "https://clscor.io/entity/type/appellation/artificial_title"
            )
            yield (
                mkuri(f"{self.title} [Title]"),
                crm.P2_has_type,
                artificial_title
            )

    def f123_triples(self) -> Iterator[_Triple]:
        """Triple generator for F1, F2, F3 assertions."""
        f1_triples = ttl(
            self.namespace.f1,
            (RDF.type, lrm.F1_Work),
            (RDFS.label, Literal(f"{self.title} [Work Title]")),
            (lrm.R3_is_realized_in, self.namespace.f2)
        )

        f2_triples = ttl(
            self.namespace.f2,
            (RDF.type, lrm.F2_Expression),
            (RDFS.label, Literal(f"{self.title} [Expression Title]")),
            (lrm.R41_is_embodied_in, (self.namespace.f3, self.namespace.x2))
        )

        f3_triples = ttl(
            self.namespace.f3,
            (RDF.type, lrm.F3_Manifestation),
            (RDFS.label, Literal(f"{self.title} [Manifestation]")),
            (lrm.R24i_was_created_through, self.namespace.f30)
        )

        triples = itertools.chain(
            f1_triples,
            f2_triples,
            f3_triples
        )

        return triples

    def x2_triples(self) -> Iterator[_Triple]:
        """Triple generator for X2 triples."""
        return ttl(
            self.namespace.x2,
            (RDF.type, clscore.X2_Corpus_Document),
            (RDFS.label, Literal(f"{self.title} [Corpus Document Title]")),
            (lrm.R4_embodies, self.namespace.f2),
            (lrm.R71i_is_part_of, self.namespace.x1_dlk),
            (lrm.P148i_is_component_of, self.namespace.x1_dlk),
            (crm.P137_exemplifies, self.namespace.x11_dlk),
            (crm.P72_has_language, URIRef("https://vocabs.acdh.oeaw.ac.at/iso6391/de")),
            (crm.P1_is_identified_by, (
                [
                    (RDF.type, crm.E42_Identifier),
                    (RDFS.label, Literal(f"{self.bindings.dlk_id} [DLK ID]")),
                    (crm.P190_has_symbolic_content, Literal(f"{self.bindings.dlk_id}")),
                    (crm.P2_has_type, self.namespace.e55_id)
                ],
                [
                    (RDF.type, crm.E42_Identifier),
                    (RDFS.label, Literal(f"{self.bindings.resource_uri} [DLK ID URL]")),
                    (crm.P190_has_symbolic_content, Literal(f"{self.bindings.resource_uri}")),
                    (crm.P2_has_type, self.namespace.e55_id_url)
                ]
            ))
        )

    def lrm_e2_triples(self) -> Iterator[_Triple]:
        """Triple generator for F27, F28, F30 triples."""
        author_uris: tuple[URIRef, ...] = tuple(self.authors_mapping.values())

        f27_triples = ttl(
            self.namespace.f27,
            (RDF.type, lrm.F27_Work_Creation),
            (RDFS.label, Literal(f"{self.title} [Work Creation]")),
            (lrm.R16_created, self.namespace.f1),
            (lrm.P14_carried_out_by, author_uris)
        )

        f28_triples = ttl(
            self.namespace.f28,
            (RDF.type, lrm.F28_Expression_Creation),
            (RDFS.label, Literal(f"{self.title} [Expression Creation]")),
            (lrm.R17_created, self.namespace.f2),
            (crm.P14_carried_out_by, author_uris)
        )

        f30_triples = ttl(
            self.namespace.f30,
            (RDF.type, lrm.F30_Manifestation_Creation),
            (lrm.R24_created, self.namespace.f3),
            (crm.P14_carried_out_by, author_uris),
            (crm["P4_has_time-span"], [
                (RDF.type, crm["E52_Time-Span"]),
                (
                    crm.P82_at_some_time_within,
                    Literal(
                        f"{self.bindings.publication_date}",
                        datatype=XSD.gYear
                    )
                )
            ])
        )

        triples = itertools.chain(
            f27_triples,
            f28_triples,
            f30_triples
        )

        return triples

    def e39_triples(self) -> Iterator[_Triple]:
        """Triple generator for E39 Authors triples."""
        for author_name, author_uri in self.authors_mapping.items():
            yield from ttl(
                author_uri,
                (RDF.type, crm.E39_Author),
                (RDFS.label, Literal(f"{author_name} [Actor]")),
                (crm.P1_is_identified_by, [
                    (RDF.type, crm.E41_Appellation),
                    (crm.P190_has_symbolic_content, Literal(f"{author_name} [Actor]"))
                ])
            )


def dlk_static_triples(
        bindings: DLKBindingsModel,
        namespace: URINamespace
) -> Iterator[_Triple]:
    """Generate static E55 triples for DLK."""
    e55_id_triples = ttl(
        namespace.e55_id,
        (RDF.type, crm.E55_Type),
        (RDFS.label, Literal("DLK Document ID"))
    )

    e55_id_url_triples = ttl(
        namespace.e55_id_url,
        (RDF.type, crm.E55_Type),
        (RDFS.label, Literal("DLK Document ID URL"))
    )

    triples = itertools.chain(
        e55_id_triples,
        e55_id_url_triples
    )

    return triples
