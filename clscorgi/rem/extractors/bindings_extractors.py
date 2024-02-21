"""ReM bindings extractors"""

from collections.abc import Callable
from pathlib import Path

from lxml import etree
from toolz import valmap

from clscorgi.bindings_abc import BindingsExtractor
from clscorgi.rem.extractors.tree_extractors import (
    get_id,
    get_title,
    get_genre,
    get_token,
    get_publication,
    get_source
)

class ReMBindingsExtractor(BindingsExtractor):
    def __init__(self, header_path: Path):
        self.header_path = header_path
        super().__init__()

    def generate_bindings(self) -> dict:
        tree = etree.parse(self.header_path)

        _bindings_mapping: dict[str, Callable] = {
            "id": get_id,
            "title": get_title,
            "genre": get_genre,
            "token_count": get_token,
            "publication": get_publication,
            "soure": get_source
        }

        bindings = valmap(lambda x: x(tree), _bindings_mapping)
        return bindings
