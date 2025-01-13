"""Triple generators for Tool Inventory table to RDF conversion."""

import abc
from collections.abc import Iterator
from functools import partial
from importlib.resources import files
from itertools import chain

from lodkit import _Triple, ttl
import numpy as np
import pandas as pd
from rdflib import Graph, Literal, RDF, RDFS, URIRef


_data_path = files("clscorgi.tool_inventory.data") / "tool_inventory.csv"
df = pd.read_csv(_data_path)

ttl = partial(ttl, skip_if=lambda s, p, o: pd.isna(o))


class _ABCRowConverter(abc.ABC):
    def __init__(self, series: pd.Series) -> None:
        self.series = series
        self._iter = iter(self)

    @abc.abstractmethod
    def __iter__(self) -> Iterator[_Triple]:
        raise NotImplementedError

    def __next__(self) -> _Triple:
        return next(self._iter)


class _TaskDescriptionRowConverter(_ABCRowConverter):
    def __iter__(self) -> Iterator[_Triple]:
        return chain(self._generate_task_description_triples())

    def _generate_task_description_triples(self):
        return ttl(
            URIRef("TaskDescSubject"),
            (URIRef("predicate_1"), "ok"),
            (URIRef("predicate_1"), np.nan),
        )


class ToolInventoryRowConverter(_ABCRowConverter):
    def __iter__(self) -> Iterator[_Triple]:
        return chain(
            self.generate_some_triples(), self.generate_task_description_triples()
        )

    def generate_some_triples(self):
        return ttl(
            URIRef("subject"),
            (URIRef("predicate"), "literal"),
            (URIRef("predicate"), np.nan),
        )

    def generate_task_description_triples(self):
        task_desc_df = df  # will be the respective sheet

        for _, row in task_desc_df.iterrows():
            yield from _TaskDescriptionRowConverter(row)


graph = Graph()

for _, row in df.iterrows():
    for triple in ToolInventoryRowConverter(row):
        graph.add(triple)


print(graph.serialize())
