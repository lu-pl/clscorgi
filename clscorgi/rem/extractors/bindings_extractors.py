"""ReM bindings extractors"""

from collections.abc import Callable
from pathlib import Path

from clscorgi.bindings_abc import BindingsExtractor
from clscorgi.rem.extractors.tree_extractors import (get_genre, get_id,
                                                     get_publication,
                                                     get_resource_url,
                                                     get_source, get_title,
                                                     get_token)
from clscorgi.utils.utils import revalmap
from lxml import etree
from toolz import compose, valmap

value_sanitizer = compose(
    lambda x: None if x in ("-", "NA", "") else x
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
            "resource_url": get_resource_url,
            "publication": get_publication,
            "source": get_source,
        }

        _bindings = valmap(lambda x: x(tree), _bindings_mapping)
        bindings = revalmap(value_sanitizer, _bindings)
        return bindings
