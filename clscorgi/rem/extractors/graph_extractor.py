"""Script for extracting and persisting ReM data as JSON."""

import json

from collections.abc import Callable
from functools import reduce
from importlib.resources import files
from os import PathLike
from pathlib import Path, PosixPath

from functools import reduce
from rdflib import Graph


def _get_query_template(crm_class):
    query_template = (
        "select distinct ?id1 ?id2"
        "where {"
        "?s ?p ?o ; "
        f"a {crm_class} . "
        "optional {?s owl:sameAs ?id1}"
        "optional {?s rdfs:seeAlso ?id2}"
        "}"
    )

    return query_template


def _get_external_id_factory(crm_class) -> Callable[[Graph], list | None]:
    template = _get_query_template(crm_class)

    def _wrapper(graph: Graph):
        query_results = graph.query(template)
        result = [
            str(unification)
            for query_result in query_results
            for unification in query_result
            if unification is not None
        ] or None

        return result
    return _wrapper


_get_work_ids = _get_external_id_factory("frbroo:F1_Work")
_get_author_ids = _get_external_id_factory("crm:E39_Actor")


def _graph_extractor(graph_file: Path) -> dict:
    rem_id = graph_file.stem
    graph = Graph().parse(graph_file)

    author_ids = _get_author_ids(graph)
    work_ids = _get_work_ids(graph)

    if not (author_ids or work_ids):
        return {}
    return {
        rem_id: {
            "author_ids": author_ids,
            "work_ids": work_ids
        }
    }


if __name__ == "__main__":
    graph_dir = files("clscorgi.rem.data.graphs")
    output_file = files("clscorgi.rem.data") / "external_ids.json"

    graph_data = reduce(
        lambda d, data: d | data,
        map(_graph_extractor, graph_dir.iterdir()),
        dict()
    )

    with open(output_file, "w") as f:
        json.dump(graph_data, f, indent=4)
