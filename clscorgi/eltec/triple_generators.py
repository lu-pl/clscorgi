"""Triple generators for ELTeC corpora."""

from collections.abc import Iterator
from contextlib import suppress
from itertools import chain
from typing import Self

from lodkit import URINamespace, ttl, mkuri_factory, _Triple
from clisn import lrm, crm, clscore, crmcls

from rdflib import Literal
from rdflib.namespace import RDF, RDFS

from clscorgi.models import ELTeCBindingsModel
from clscorgi.vocabs.vocabs import VocabLookupException, vocab
from clscorgi.utils.utils import resolve_source_type


mkuri = mkuri_factory(clscore)


class eltec_f3_triples:
    def __init__(
            self,
            bindings: ELTeCBindingsModel,
            namespace: URINamespace
    ) -> None:
        self.bindings = bindings
        self.namespace = namespace

    def __iter__(self) -> Iterator[_Triple]:
        for work_id in self.bindings.work_ids:
            yield from self.f3_triples(work_id)
            yield from self.e42_triples(work_id)

    def __next__(self) -> _Triple:
        return next(self)

    def f3_triples(self, work_id):
        yield from ttl(
            mkuri(f"f3 {work_id.id_value}"),
            (RDF.type, lrm.F3_Manifestation),
            (
                RDFS.label,
                Literal(f"{self.bindings.work_title} [Manifestation]")
            ),
            (crm.P1_is_identified_by, mkuri(f"e42 {work_id.id_value}")),
            (lrm.R4_embodies, self.namespace.f2),
        )

        with suppress(VocabLookupException):
            source_type: str = resolve_source_type(
                work_id.source_type
            )
            vocab_uri = vocab(source_type)
            yield (
                mkuri(f"f3 {work_id.id_value}"),
                crm.P2_has_type,
                vocab_uri
            )

    def e42_triples(self, work_id):
        yield from ttl(
            mkuri(f"e42 {work_id.id_value}"),
            (RDF.type, crm.E42_Identifier),
            (RDFS.label, Literal(f"{self.bindings.work_title} [ID]")),
            (crm.P190_has_symbolic_content, Literal(f"{work_id.id_value}"))
        )

        with suppress(VocabLookupException):
            vocab_uri = vocab(work_id.id_type)
            yield (
                mkuri(f"e42 {work_id.id_value}"),
                crm.P2_has_type,
                vocab_uri
            )


def eltec_wemi_triples(
        bindings: ELTeCBindingsModel,
        namespace: URINamespace
) -> Iterator[_Triple]:
    """Triple generator for ELTeC LRM boilerplate."""
    f1_triples = ttl(
        namespace.f1,
        (RDF.type, lrm.F1_Work),
        (RDFS.label, Literal(f"{bindings.work_title} [Work]")),
        (lrm.R16i_was_created_by, namespace.f27),
        (lrm.R3_is_realised_in, namespace.f2),
        (lrm.R74i_has_expression_used_in, namespace.f1)
    )

    f2_triples = ttl(
        namespace.f2,
        (RDF.type, lrm.F2_Expression),
        (RDFS.label, Literal(f"{bindings.work_title} [Expression]")),
        (crm.P102_has_title, namespace.e35),
        (lrm.R3i_realises, namespace.f1),
        (lrm.R17i_was_created_by, namespace.f28)
    )

    ## todo: this should be done in f3 triple generator
    # (lrm.R4i_is_embodied_in, (namespace.x2, *f3_uris))

    x1_triples = ttl(
        mkuri(bindings.repo_id),
        ## todo: crmcls vs. clscore?!
        (RDF.type, crmcls.X1_Corpus),
        (crm.P1_is_identified_by, ttl(
            mkuri(f"{bindings.repo_id} [X1 Appellation]"),
            (RDF.type, crm.E41_Appellation),
            (RDF.value, Literal(f"ELTeC {bindings.repo_id.split('-')[1].upper()}"))
        )),
        (lrm.R71_has_part, namespace.x2),
        (crmcls.Y4i_is_subcorpus_of, namespace.x1_eltec)
    )

    x1_eltec_triples = ttl(
        namespace.x1_eltec,
        (RDF.type, crmcls.X1_Corpus),
        (crmcls.Y4_has_subcorpus, mkuri(bindings.repo_id)),
        (crm.P148_has_component, namespace.x2)
    )

    x2_triples = ttl(
        namespace.x2,
        (RDF.type, crmcls.X2_Corpus_Document),
        (RDFS.label, Literal(f"{bindings.work_title} [TEI Document]")),
        (crm.P1_is_identified_by, namespace.x2_e42),
        (lrm.R4_embodies, namespace.f2),
        (lrm.R71i_is_part_of, mkuri(bindings.repo_id)),
        (crmcls.Y2_has_format, vocab("TEI")),
        (crmcls.Y3_adheres_to_schema, namespace.x8_eltec),
        (crm.P137_exemplifies, namespace.x11_eltec)
    )

    x2_e42_triples = ttl(
        namespace.x2_e42,
        (RDF.type, crm.E42_Identifier),
        (RDFS.label, Literal(f"{bindings.work_title} [ELTeC ID]")),
        (crm.P190_has_symbolic_content, Literal(f"{bindings.file_stem}")),
        (crm.P2_has_type, mkuri("ELTeC Title"))
    )

    triples = chain(
        f1_triples,
        f2_triples,
        x1_triples,
        x1_eltec_triples,
        x2_triples,
        x2_e42_triples
    )

    return triples
