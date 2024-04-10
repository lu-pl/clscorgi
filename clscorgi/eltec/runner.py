"""ELTeC runner: Main entry point for ELTeC conversions."""

import json

from collections.abc import Iterator
from os import PathLike
from pathlib import Path

from importlib.resources import files

from clisn import CLSInfraNamespaceManager
from lodkit.graph import Graph
from loguru import logger

from clscorgi.eltec.extractors.bindings_extractor import ELTeCBindingsExtractor
from clscorgi.eltec.extractors.link_extractor import get_eltec_xml_links
from clscorgi.rdfgenerators import ELTeCRDFGenerator


def eltec_runner() -> None:
    """ELTeC runner."""
    input_files: dict[str, Path] = {
        input_file.stem: input_file
        for input_file in files("clscorgi.eltec.data.generated").iterdir()
        if input_file.name.split(".")[-1] == "json"
    }

    for input_name, input_file in input_files.items():
        with open(input_file) as input_f:
            input_json = json.load(input_f)

        g = Graph()
        CLSInfraNamespaceManager(g)

        for data in input_json:
            triples = ELTeCRDFGenerator(**data)

            for triple in triples:
                g.add(triple)

        output_dir = files("clscorgi.output.eltec")
        output_file = output_dir / f"{input_name}.ttl"
        with open(output_file, "w") as f:
            f.write(g.serialize())
