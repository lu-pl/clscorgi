"""Functionality for parsing ELTeC XML file links and extracting bindings."""

import collections
from dataclasses import InitVar, dataclass
from pathlib import Path
from urllib.request import urlretrieve

from clscorgi.bindings_abc import BindingsExtractor
from clscorgi.eltec.extractors.tree_extractors import (get_author_ids,
                                                       get_author_name,
                                                       get_date, get_work_ids,
                                                       get_work_title)
from lxml import etree


@dataclass
class ELTeCPath:
    """Object representation for ELTeC raw links."""
    _eltec_url: InitVar

    def __post_init__(self, eltec_url):
        """Postinit hook for ELTeCPath."""
        _path = Path(eltec_url)

        self.url = eltec_url
        self.stem = _path.stem.lower()
        self.repo_id = _path.parts[3].lower()


class ELTeCBindingsExtractor(BindingsExtractor):
    """Binding Representation for an ELTeC resource."""

    def __init__(self, eltec_url: str) -> None:
        """Initialize a BindingExtractor object."""
        self._eltec_url = self._quote_iri(eltec_url)
        self._eltec_path = ELTeCPath(eltec_url)

        super().__init__()

    def generate_bindings(self) -> dict:
        """Construct kwarg bindings for RDF generation."""
        _temp_file_name, _ = urlretrieve(self._eltec_url)

        with open(_temp_file_name) as f:
            tree = etree.parse(f)

        bindings = {
            "resource_uri": self._eltec_path.url,
            "file_stem": self._eltec_path.stem,
            "repo_id": self._eltec_path.repo_id,

            "work_title": get_work_title(tree),
            "author_name": get_author_name(tree),

            "work_ids": get_work_ids(tree),
            "author_ids": get_author_ids(tree),

            "date": get_date(tree)
        }

        return bindings
