"""Triple generators for the DLK corpus."""

import itertools
from collections.abc import Iterator

from clisn import clscore, crm, lrm
from clscorgi.models import DLKBindingsModel
from lodkit import URINamespace, _Triple, mkuri_factory, ttl
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS

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
        self.title = self.bindings.title or self.bindings.first_line

    def __next__(self) -> _Triple: # noqa
        return next(self)

    def __iter__(self) -> Iterator[_Triple]: # noqa
        yield from self.f123_triples()
        yield from self.e35_triples()
        yield from self.x2_triples()

    def e35_triples(self):
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

    def f272830_triples(self):
        """Triple generator for F27, F28, F30 triples."""
        pass


def static_triples(
        bindings: DLKBindingsModel,
        namespace: URINamespace
) -> Iterator[_Triple]:
    """Generate static E55 triples for DLK."""
    pass
