"""Triple generators for Tool Inventory table to RDF conversion."""

import abc
from collections.abc import Iterator
from importlib.resources import files
from itertools import chain

from clscorgi.vocabs.vocab_lookup import vocabs
from lodkit import NamespaceGraph, URIConstructorFactory, _Triple, ttl
import numpy as np
import pandas as pd
from rdflib import Literal, Namespace, RDF, URIRef, XSD


crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmcls = Namespace("https://clscor.io/ontologies/CRMcls/")

mkuri = URIConstructorFactory("https://clscor.io/entity/")


class _ABCRowConverter(abc.ABC):
    def __init__(self, series: pd.Series) -> None:
        self.series = series

        self.tool_uri = mkuri(self.series["toolname"])
        self.tool_descevent_uri = mkuri(f"{self.series['toolname']} descevent")

        self._iter = iter(self)

    @abc.abstractmethod
    def __iter__(self) -> Iterator[_Triple]:
        raise NotImplementedError

    def __next__(self) -> _Triple:
        return next(self._iter)


class _TaskDescriptionRowConverter(_ABCRowConverter):
    def __iter__(self) -> Iterator[_Triple]:
        return chain(self._generate_task_description_triples())

    def _generate_task_description_triples(self) -> Iterator[_Triple]:
        return ttl(
            URIRef("TaskDescSubject"),
            (crm.P1_is_identified_by, "ok"),
            (URIRef("predicate_1"), np.nan),
        )


class ToolInventoryRowConverter(_ABCRowConverter):
    def __iter__(self) -> Iterator[_Triple]:
        return chain(
            self.generate_appellation_triples(),
            self.generate_tool_description_triples(),
            self.generate_tool_descevent_triples(),
            self.generate_primary_purpose_triples(),
            self.generate_version_note_triples(),
            self.generate_version_date_triples(),
        )

    def generate_appellation_triples(self) -> Iterator[_Triple]:
        yield from ttl(
            self.tool_uri,
            (RDF.type, crmcls.X12_Tool),
            (
                crm.P1_is_identified_by,
                ttl(
                    mkuri(),
                    (RDF.type, crm.E42_Appellation),
                    (crm.P2_has_type, vocabs.appellation("tool name")),
                    (RDF.value, self.series["toolname"]),
                ),
            ),
        )

        if (alternate_name := self.series["alternate name"]) is not np.nan:
            yield from ttl(
                self.tool_uri,
                (
                    crm.P1_is_identified,
                    ttl(
                        mkuri(),
                        (RDF.type, crm.E42_Appellation),
                        (crm.P2_has_type, vocabs.appellation("alternate tool name")),
                        (RDF.value, alternate_name),
                    ),
                ),
            )

    def generate_tool_description_triples(self) -> Iterator[_Triple]:
        tool_description_literal: str = self.series["what can this tool do for you?"]

        return ttl(
            mkuri(tool_description_literal),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["tool_description"]),
            (crm["P03_has_range_literal"], tool_description_literal),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_tool_descevent_triples(self) -> Iterator[_Triple]:
        return ttl(
            self.tool_descevent_uri,
            (RDF.type, crmcls.X13_Tool_Description),
            (
                crm.P16_used_specific_object,
                (
                    URIRef("https://doi.org/10.5281/zenodo.7951060"),
                    URIRef("https://doi.org/10.5281/zenodo.11094000"),
                ),
            ),
            # (crm.P14_carried_out_by)
            (
                crm["P4_has_time-span"],
                [
                    (RDF.type, crm["E52_Time-Span"]),
                    (
                        crm.P81a_end_of_the_begin,
                        Literal("2013-03-09", datatype=XSD.date),
                    ),
                    (
                        crm.P81b_begin_of_the_end,
                        Literal("2025-01-31", datatype=XSD.date),
                    ),
                ],
            ),
        )

    def generate_primary_purpose_triples(self) -> Iterator[_Triple]:
        methods = tuple(
            vocabs.method(value.strip())
            for value in self.series["primary_purpose_consolidated_CLSCor_vocab"].split(
                ","
            )
        )

        return ttl(
            mkuri(),
            (RDF.type, crm.E13_Attribute_Assignment),
            (crm.P134_continued, self.tool_descevent_uri),
            (crm.P140_assigned_attribute_to, self.tool_uri),
            (crm.P141_assigned, methods),
            (crm.P177_assigned_property_of_type, crmcls.Y8_implements),
        )

    def generate_version_note_triples(self) -> Iterator[_Triple]:
        note_literal = self.series["Version_consolidated"]

        return ttl(
            mkuri(note_literal),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["version"]),
            (crm["P03_has_range_literal"], note_literal),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_version_date_triples(self) -> Iterator[_Triple]:
        date_literal = self.series["Version Date_consolidated"]

        return ttl(
            mkuri(date_literal),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["version_date"]),
            (crm["P03_has_range_literal"], date_literal),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_task_description_triples(self):
        task_desc_df = df  # will be the respective sheet

        for _, row in task_desc_df.iterrows():
            yield from _TaskDescriptionRowConverter(row)


##################################################
#### runner logic

_data_path = files("clscorgi.tool_inventory.data") / "tool_inventory.csv"
df = pd.read_csv(_data_path)


class CLSGraph(NamespaceGraph):
    crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
    crmcls = Namespace("https://clscor.io/ontologies/CRMcls/")
    clscor = Namespace("https://clscor.io/entity/")


graph = CLSGraph()

for _, row in df.iterrows():
    for triple in ToolInventoryRowConverter(row):
        graph.add(triple)


print(graph.serialize())
