"""Script for extracting and persisting ReM data as JSON."""

import json

from importlib.resources import files
from clscorgi.rem.extractors.bindings_extractors import ReMBindingsExtractor


xml_dir = files("clscorgi.rem.data.headers")
data_file = files("clscorgi.rem.data.generated") / "rem.json"


if __name__ == "__main__":
    bindings = [
        dict(ReMBindingsExtractor(xml_file))
        for xml_file
        in xml_dir.iterdir()
    ]

    with open(data_file, "w") as f:
        json.dump(bindings, f, indent=4)
