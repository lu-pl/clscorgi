"""Triple generators for Tool Inventory table to RDF conversion."""

import abc
from collections.abc import Iterator
from importlib.resources import files
from itertools import chain
from pathlib import Path

from clscorgi.tool_inventory.data.actor_data import actors
from clscorgi.utils.utils import get_language_uri
from clscorgi.vocabs.vocab_lookup import vocabs
from lodkit import NamespaceGraph, URIConstructorFactory, _Triple, ttl
import numpy as np
import pandas as pd
from rdflib import Literal, Namespace, RDF, RDFS, URIRef, XSD


crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmcls = Namespace("https://clscor.io/ontologies/CRMcls/")
clscor = Namespace("https://clscor.io/entity/")

mkuri = URIConstructorFactory("https://clscor.io/entity/")


class _ABCRowConverter(abc.ABC):
    """ABC for pd.Series to RDF conversions.

    Basically just an initializer and the iterator protocol.
    Note: It is important that self._iter gets defined last
    in the initializer; other init vars won't be accessible upon iteration.
    """

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


class _MethodsRowConverter(_ABCRowConverter):
    """RowConverter for the 'methods' table."""

    def __iter__(self) -> Iterator[_Triple]:
        return chain(self._generate_task_description_triples())

    def _generate_task_description_triples(self) -> Iterator[_Triple]:
        return ttl(
            mkuri(self.series["toolname"]),
            (
                crm.P1_is_identified_by,
                self.series["methods_used_consolidated CLSCor vocab"],
            ),
        )


class ToolInventoryRowConverter(_ABCRowConverter):
    """RowConverter for the main table.

    RowConverters for sheets are looked up and called
    from methods of this main RowConverter.
    """

    def __iter__(self) -> Iterator[_Triple]:
        return chain(
            self.generate_appellation_triples(),
            self.generate_tool_description_triples(),
            self.generate_tool_descevent_triples(),
            self.generate_primary_purpose_triples(),
            self.generate_version_note_triples(),
            self.generate_version_date_triples(),
            self.generate_distribution_triples(),
            self.generate_user_interface_triples(),
            self.generate_tool_processing_triples(),
            self.generate_output_format_triples(),
            self.generate_input_format_triples(),
            self.generate_metric_triples(),
            self.generate_visualisation_triples(),
            self.generate_formalism_triples(),
            self.generate_tagset_triples(),
            self.generate_statistical_models_triples(),
            self.generate_license_triples(),
            self.generate_os_triples(),
            self.generate_language_triples(),
            self.generate_tool_integration_triples(),
            #
            # self.generate_methods_triples(),
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
        tool_description_literal: str = self.series["tool_description"]

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
            (crm.P14_carried_out_by, tuple(actor.uri for actor in actors)),
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

    def generate_distribution_triples(self) -> Iterator[_Triple]:
        if (distribution_literal := self.series["Distribution"]) is np.nan:
            return

        yield from ttl(
            mkuri(distribution_literal),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["distribution"]),
            (crm["P03_has_range_literal"], distribution_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_user_interface_triples(self) -> Iterator[_Triple]:
        if (userinterface_literal := self.series["User interface"]) is np.nan:
            return

        yield from ttl(
            mkuri(userinterface_literal),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["user_interface"]),
            (crm["P03_has_range_literal"], userinterface_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_tool_processing_triples(self) -> Iterator[_Triple]:
        if (
            toolprocessing_literal := self.series["How does the tool process your text"]
        ) is np.nan:
            return

        yield from ttl(
            mkuri(toolprocessing_literal),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["tool_processing"]),
            (crm["P03_has_range_literal"], toolprocessing_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_output_format_triples(self) -> Iterator[_Triple]:
        if (
            output_format := self.series["output_format (consolidated CLSCor vocab)"]
        ) is np.nan:
            return

        e13_uri = mkuri()
        formats = tuple(
            vocabs.format(value.strip()) for value in output_format.split(",")
        )

        yield from ttl(
            e13_uri,
            (RDF.type, crm.E13_Attribute_Assignment),
            (crm.P134_continued, self.tool_descevent_uri),
            (crm.P140_assigned_attribute_to, self.tool_uri),
            (crm.P141_assigned, formats),
            (crm.P177_assigned_property_of_type, crmcls.Y10_generates_output),
        )

        if (output_comment := self.series["output_format_comment"]) is not np.nan:
            yield from ttl(e13_uri, (crm.P3_has_note, output_comment.strip()))

    def generate_input_format_triples(self) -> Iterator[_Triple]:
        if (
            input_format := self.series["input_format (consolidated CLSCor vocab)"]
        ) is np.nan:
            return

        e13_uri = mkuri()
        formats = tuple(
            vocabs.format(value.strip()) for value in input_format.split(",")
        )

        yield from ttl(
            e13_uri,
            (RDF.type, crm.E13_Attribute_Assignment),
            (crm.P134_continued, self.tool_descevent_uri),
            (crm.P140_assigned_attribute_to, self.tool_uri),
            (crm.P141_assigned, formats),
            (crm.P177_assigned_property_of_type, crmcls.Y9_expects_input),
        )

        if (input_comment := self.series["input_format_comment"]) is not np.nan:
            yield from ttl(e13_uri, (crm.P3_has_note, input_comment.strip()))

    def generate_metric_triples(self) -> Iterator[_Triple]:
        if (metric_literal := self.series["metric"]) is np.nan:
            return

        yield from ttl(
            mkuri(metric_literal),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["metric"]),
            (crm["P03_has_range_literal"], metric_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_visualisation_triples(self) -> Iterator[_Triple]:
        if (visualisation_literal := self.series["visualisation"]) is np.nan:
            return

        yield from ttl(
            mkuri(visualisation_literal),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["visualisation"]),
            (crm["P03_has_range_literal"], visualisation_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_formalism_triples(self) -> Iterator[_Triple]:
        if (formalism_literal := self.series["formalism"]) is np.nan:
            return

        yield from ttl(
            mkuri(formalism_literal),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["formalism"]),
            (crm["P03_has_range_literal"], formalism_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_tagset_triples(self) -> Iterator[_Triple]:
        if (tagset_literal := self.series["tagset"]) is np.nan:
            return

        yield from ttl(
            mkuri(tagset_literal),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["tagset"]),
            (crm["P03_has_range_literal"], tagset_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_statistical_models_triples(self) -> Iterator[_Triple]:
        if (statistical_models_literal := self.series["statistical_models"]) is np.nan:
            return

        yield from ttl(
            mkuri(statistical_models_literal),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["statistical_models"]),
            (crm["P03_has_range_literal"], statistical_models_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_license_triples(self) -> Iterator[_Triple]:
        if (license := self.series["License (consolidated CLSCor vocab)"]) is np.nan:
            return

        e13_uri = mkuri()
        licenses = tuple(vocabs.licenses(value.strip()) for value in license.split(","))

        yield from ttl(
            e13_uri,
            (RDF.type, crm.E13_Attribute_Assignment),
            (crm.P134_continued, self.tool_descevent_uri),
            (crm.P140_assigned_attribute_to, self.tool_uri),
            (crm.P141_assigned, licenses),
            (crm.P177_assigned_property_of_type, crm.P2_has_type),
        )

        if (output_comment := self.series["License_comment"]) is not np.nan:
            yield from ttl(e13_uri, (crm.P3_has_note, output_comment.strip()))

    def generate_os_triples(self) -> Iterator[_Triple]:
        if (
            operating_system := self.series[
                "Works on Operating Systems (consolidated CLSCor vocab)"
            ]
        ) is np.nan:
            return

        e13_uri = mkuri()
        operating_system = tuple(
            vocabs.operating_system(value.strip())
            for value in operating_system.split(",")
        )

        yield from ttl(
            e13_uri,
            (RDF.type, crm.E13_Attribute_Assignment),
            (crm.P134_continued, self.tool_descevent_uri),
            (crm.P140_assigned_attribute_to, self.tool_uri),
            (crm.P141_assigned, operating_system),
            (crm.P177_assigned_property_of_type, crm.P2_has_type),
        )

        if (
            output_comment := self.series["Works on Operating Systems_comment"]
        ) is not np.nan:
            yield from ttl(e13_uri, (crm.P3_has_note, output_comment.strip()))

    def generate_language_triples(self) -> Iterator[_Triple]:
        if (language_data := self.series["Language_consolidated"]) is np.nan:
            return

        e13_uri = mkuri()
        language_iso_uris = {
            name: get_language_uri(name.strip()) for name in language_data.split(",")
        }

        for name, uri in language_iso_uris.items():
            yield (uri, RDFS.label, Literal(name.strip()))

        yield from ttl(
            e13_uri,
            (crm.P134_continued, self.tool_descevent_uri),
            (crm.P140_assigned_attribute_to, self.tool_uri),
            (crm.P141_assigned, tuple(language_iso_uris.values())),
            (crm.P177_assigned_property_of_type, crm.P72_has_language),
        )

        if (language_comment := self.series["Language_comment"]) is np.nan:
            return

        yield from ttl(e13_uri, (crm.P3_has_note, language_comment.strip()))

    def generate_tool_integration_triples(self) -> Iterator[_Triple]:
        if (
            tool := self.series[
                "Which other tools from this list does this tool integrate?"
            ]
        ) is np.nan:
            return

        tools = tuple(mkuri(value.strip()) for value in tool.split(","))
        yield from ttl(self.tool_uri, (crmcls.Y7_uses, tools))

    ## other sheet
    def generate_methods_triples(self):
        """Triple generator for another sheet.

        This generator needs to look up the applicable rows
        in the respective sheet and loop + yield from those series.
        """
        df_methods: pd.DataFrame = pd.read_csv(_data_path / "methods.csv")
        partition: pd.DataFrame = df_methods[df_methods["id"] == self.series["id"]]

        for _, row in partition.iterrows():
            yield from _MethodsRowConverter(row)


def generate_actor_triples() -> Iterator[_Triple]:
    """Generator for static actor triples.

    Those triples need to get generated only once per run
    and not once per table row.
    """
    for actor in actors:
        yield from ttl(actor.uri, (RDF.type, crm.E39_Actor), (RDFS.label, actor.name))

        if (note := actor.note) is not None:
            yield (actor.uri, crm.P3_has_note, Literal(note))


##################################################
#### runner logic

_data_path = files("clscorgi.tool_inventory.data")
df_tool_inventory = pd.read_csv(_data_path / "tool_inventory.csv")


class CLSGraph(NamespaceGraph):
    crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
    crmcls = Namespace("https://clscor.io/ontologies/CRMcls/")
    clscor = Namespace("https://clscor.io/entity/")


graph = CLSGraph()

actor_triples = generate_actor_triples()
table_triples = chain.from_iterable(
    ToolInventoryRowConverter(row) for _, row in df_tool_inventory.iterrows()
)

for triple in chain(table_triples, actor_triples):
    graph.add(triple)
