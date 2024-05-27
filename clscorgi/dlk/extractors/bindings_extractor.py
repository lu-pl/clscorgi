"""Binding extractor for the DLK corpus."""

import re
from dataclasses import InitVar, dataclass
from pathlib import Path
from urllib.request import urlretrieve

from clscorgi.bindings_abc import BindingsExtractor
from clscorgi.dlk.extractors.tree_extractors import (get_author_names,
                                                     get_features,
                                                     get_first_line, get_title,
                                                     get_urn)
from lxml import etree


@dataclass
class DLKPath:
    """Object representation for DLK raw links."""

    _eltec_url: InitVar

    def __post_init__(self, dlk_url):
        """Postinit hook for DLKPath."""
        self.url = dlk_url
        # todo: regex needs revision
        self.dlk_id = re.search(r".+/([\w.]+)-.+", dlk_url).group(1)


class DLKBindingsExtractor(BindingsExtractor):
    """Binding Representation for a DLK resource."""

    def __init__(self, dlk_url: str):
        self.dlk_url = self._quote_iri(dlk_url)
        # self.dlk_url = dlk_url
        self.dlk_path = DLKPath(dlk_url)

        super().__init__()

    def generate_bindings(self) -> dict:
        """Construct kwarg bindings for RDF generation."""
        _temp_file_name, _ = urlretrieve(self.dlk_url)

        with open(_temp_file_name) as f:
            tree = etree.parse(f)

        bindings = {
            "resource_uri": self.dlk_path.url,
            "urn": get_urn(tree),
            "dlk_id": self.dlk_path.dlk_id,
            "authors": list(get_author_names(tree)),
            "title": get_title(tree),
            "first_line": get_first_line(tree),
            "features_dlk": get_features(tree)
        }

        return bindings
