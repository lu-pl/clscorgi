"""Triple generators for Tool Inventory table to RDF conversion."""

import abc
from collections.abc import Iterator
from importlib.resources import files
from itertools import chain

from clscorgi.tool_inventory.data.actor_data import actors
from clscorgi.utils.utils import get_language_uri
from clscorgi.vocabs.vocab_lookup import vocabs
from lodkit import NamespaceGraph, URIConstructorFactory, _Triple, ttl
import pandas as pd
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef, XSD
crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmcls = Namespace("https://clscor.io/ontologies/CRMcls/")
clscor = Namespace("https://clscor.io/entity/")

mkuri = URIConstructorFactory("https://clscor.io/entity/")
_data_path = files("clscorgi.tool_inventory.data")


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
        methods = tuple(
            vocabs.method(value.strip()) for value in self.series["method"].split(",")
        )

        e13_uri = mkuri()

        yield from ttl(
            e13_uri,
            (RDF.type, crm.E13_Attribute_Assignment),
            (crm.P134_continued, self.tool_descevent_uri),
            (crm.P140_assigned_attribute_to, self.tool_uri),
            (crm.P141_assigned, methods),
            (crm.P177_assigned_property_of_type, crmcls.Y8_implements),
        )

        if pd.isna(methods_used := self.series["method_comment"]):
            return

        yield (e13_uri, crm.P3_has_note, Literal(methods_used))


class _FeaturesRowConverter(_ABCRowConverter):
    """RowConverter for the 'featues' table."""

    def __iter__(self) -> Iterator[_Triple]:
        return chain(self._generate_feature_triples())

    def _generate_feature_triples(self) -> Iterator[_Triple]:
        features = tuple(
            vocabs.feature(value.strip()) for value in self.series["feature"].split(",")
        )

        e13_uri = mkuri()

        yield from ttl(
            e13_uri,
            (RDF.type, crm.E13_Attribute_Assignment),
            (crm.P134_continued, self.tool_descevent_uri),
            (crm.P140_assigned_attribute_to, self.tool_uri),
            (crm.P141_assigned, features),
            (crm.P177_assigned_property_of_type, crmcls.Y1_exhibits_feature),
        )

        if pd.isna(features_used := self.series["feature_comment"]):
            return

        yield (e13_uri, crm.P3_has_note, Literal(features_used))


class _RelatedPapersRowConverter(_ABCRowConverter):
    def __iter__(self) -> Iterator[_Triple]:
        return chain(self._generate_related_papers_triples())

    def _generate_related_papers_triples(self) -> Iterator[_Triple]:
        related_papers_literal = self.series["related_paper"]

        return ttl(
            mkuri(),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["related_paper"]),
            (crm["P03_has_range_literal"], related_papers_literal),
            (crm["P01_has_domain"], self.tool_uri),
        )


class _AdditionalLinkRowConverter(_ABCRowConverter):
    def __iter__(self) -> Iterator[_Triple]:
        return chain(self._generate_additional_link_triples())

    def _generate_additional_link_triples(self) -> Iterator[_Triple]:
        link = tuple(
            vocabs.link(value.strip()) for value in self.series["link_type"].split(",")
        )

        e42_uri = mkuri()

        yield from ttl(
            self.tool_uri,
            (
                crm.P1_is_identified_by,
                ttl(
                    e42_uri,
                    (RDF.type, crm.E42_Identifier),
                    (crm.P190_has_symbolic_content, self.series["link"]),
                    (crm.P2_has_type, link),
                ),
            ),
        )

        if pd.isna(link_comment := self.series["link_comment"]):
            return

        yield (e42_uri, crm.P3_has_note, Literal(link_comment))


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
            ## other sheets
            self.generate_methods_triples(),
            self.generate_features_triples(),
            self.generate_related_papers_triples(),
            self.generate_additional_link_triples(),
        )

    def generate_appellation_triples(self) -> Iterator[_Triple]:
        yield from ttl(
            self.tool_uri,
            (RDF.type, crmcls.X12_Tool),
            (
                crm.P1_is_identified_by,
                ttl(
                    mkuri(),
                    (RDF.type, crm.E41_Appellation),
                    (crm.P2_has_type, vocabs.appellation("tool name")),
                    (RDF.value, self.series["toolname"]),
                ),
            ),
        )

        if not pd.isna(alternate_name := self.series["alternate_name"]):
            yield from ttl(
                self.tool_uri,
                (
                    crm.P1_is_identified,
                    ttl(
                        mkuri(),
                        (RDF.type, crm.E41_Appellation),
                        (crm.P2_has_type, vocabs.appellation("alternate tool name")),
                        (RDF.value, alternate_name),
                    ),
                ),
            )

    def generate_tool_description_triples(self) -> Iterator[_Triple]:
        tool_description_literal: str = self.series["tool_description"]

        return ttl(
            mkuri(),
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
            for value in self.series["primary_purpose"].split(",")
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
        note_literal = self.series["version"]

        return ttl(
            mkuri(),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["version"]),
            (crm["P03_has_range_literal"], note_literal),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_version_date_triples(self) -> Iterator[_Triple]:
        date_literal = self.series["version_date"]

        return ttl(
            mkuri(),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["version_date"]),
            (crm["P03_has_range_literal"], date_literal),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_distribution_triples(self) -> Iterator[_Triple]:
        if pd.isna(distribution_literal := self.series["distribution"]):
            return

        yield from ttl(
            mkuri(),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["distribution"]),
            (crm["P03_has_range_literal"], distribution_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_user_interface_triples(self) -> Iterator[_Triple]:
        if pd.isna(userinterface_literal := self.series["user_interface"]):
            return

        yield from ttl(
            mkuri(),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["user_interface"]),
            (crm["P03_has_range_literal"], userinterface_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_tool_processing_triples(self) -> Iterator[_Triple]:
        if pd.isna(textprocessing_literal := self.series["text_processing"]):
            return

        yield from ttl(
            mkuri(),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["text_processing"]),
            (crm["P03_has_range_literal"], textprocessing_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_output_format_triples(self) -> Iterator[_Triple]:
        if pd.isna(output_format := self.series["output_format"]):
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

        if not pd.isna(output_comment := self.series["output_format_comment"]):
            yield from ttl(e13_uri, (crm.P3_has_note, output_comment.strip()))

    def generate_input_format_triples(self) -> Iterator[_Triple]:
        if pd.isna(input_format := self.series["input_format"]):
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

        if not pd.isna(input_comment := self.series["input_format_comment"]):
            yield from ttl(e13_uri, (crm.P3_has_note, input_comment.strip()))

    def generate_metric_triples(self) -> Iterator[_Triple]:
        if pd.isna(metric_literal := self.series["metric"]):
            return

        yield from ttl(
            mkuri(),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["metric"]),
            (crm["P03_has_range_literal"], metric_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_visualisation_triples(self) -> Iterator[_Triple]:
        if pd.isna(visualisation_literal := self.series["visualisation"]):
            return

        yield from ttl(
            mkuri(),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["visualisation"]),
            (crm["P03_has_range_literal"], visualisation_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_formalism_triples(self) -> Iterator[_Triple]:
        if pd.isna(formalism_literal := self.series["formalism"]):
            return

        yield from ttl(
            mkuri(),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["formalism"]),
            (crm["P03_has_range_literal"], formalism_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_tagset_triples(self) -> Iterator[_Triple]:
        if pd.isna(tagset_literal := self.series["tagset"]):
            return

        yield from ttl(
            mkuri(),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["tagset"]),
            (crm["P03_has_range_literal"], tagset_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_statistical_models_triples(self) -> Iterator[_Triple]:
        if pd.isna(statistical_models_literal := self.series["statistical_models"]):
            return

        yield from ttl(
            mkuri(),
            (RDF.type, crm.PC3_has_note),
            (crm["P3.1_has_type"], crmcls["statistical_models"]),
            (crm["P03_has_range_literal"], statistical_models_literal.strip()),
            (crm["P01_has_domain"], self.tool_uri),
        )

    def generate_license_triples(self) -> Iterator[_Triple]:
        if pd.isna(_license := self.series["license"]):
            return

        e13_uri = mkuri()
        licenses = tuple(
            vocabs.licenses(value.strip()) for value in _license.split(",")
        )

        yield from ttl(
            e13_uri,
            (RDF.type, crm.E13_Attribute_Assignment),
            (crm.P134_continued, self.tool_descevent_uri),
            (crm.P140_assigned_attribute_to, self.tool_uri),
            (crm.P141_assigned, licenses),
            (crm.P177_assigned_property_of_type, crm.P2_has_type),
        )

        if not pd.isna(output_comment := self.series["license_comment"]):
            yield from ttl(e13_uri, (crm.P3_has_note, output_comment.strip()))

    def generate_os_triples(self) -> Iterator[_Triple]:
        if pd.isna(operating_system := self.series["operating_system"]):
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

        if not pd.isna(output_comment := self.series["operating_system_comment"]):
            yield from ttl(e13_uri, (crm.P3_has_note, output_comment.strip()))

    def generate_language_triples(self) -> Iterator[_Triple]:
        if pd.isna(language_data := self.series["language"]):
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

        if pd.isna(language_comment := self.series["language_comment"]):
            return

        yield from ttl(e13_uri, (crm.P3_has_note, language_comment.strip()))

    def generate_tool_integration_triples(self) -> Iterator[_Triple]:
        if pd.isna(tool := self.series["tool_integration"]):
            return

        tools = tuple(mkuri(value.strip()) for value in tool.split(","))
        yield from ttl(self.tool_uri, (crmcls.Y7_uses, tools))

    ## other sheets
    def generate_methods_triples(self):
        """Triple generator for another sheet.

        This generator needs to look up the applicable rows
        in the respective sheet and loop + yield from those series.

        Obviously, this design is flawed, as the csv gets read and partitioned
        at ever row iteration of the main table.
        """
        df: pd.DataFrame = pd.read_csv(_data_path / "methods.csv")
        partition: pd.DataFrame = df[df["id"] == self.series["id"]]

        for _, row in partition.iterrows():
            yield from _MethodsRowConverter(row)

    def generate_features_triples(self):
        df: pd.DataFrame = pd.read_csv(_data_path / "features.csv")
        partition: pd.DataFrame = df[df["id"] == self.series["id"]]

        for _, row in partition.iterrows():
            yield from _FeaturesRowConverter(row)

    def generate_related_papers_triples(self):
        df: pd.DataFrame = pd.read_csv(_data_path / "related_papers.csv")
        partition: pd.DataFrame = df[df["id"] == self.series["id"]]

        for _, row in partition.iterrows():
            yield from _RelatedPapersRowConverter(row)

    def generate_additional_link_triples(self):
        df: pd.DataFrame = pd.read_csv(_data_path / "additional_links.csv")
        partition: pd.DataFrame = df[df["id"] == self.series["id"]]

        for _, row in partition.iterrows():
            yield from _AdditionalLinkRowConverter(row)


def generate_actor_triples() -> Iterator[_Triple]:
    """Generator for static actor triples.

    Those triples need to get generated only once per run
    and not once per table row.
    """
    for actor in actors:
        yield from ttl(actor.uri, (RDF.type, crm.E39_Actor), (RDFS.label, actor.name))

        if (note := actor.note) is not None:
            yield (actor.uri, crm.P3_has_note, Literal(note))


def generate_tool_inventory_graph() -> Graph:
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

    return graph
