"""ABC for binding generators."""

import abc
import collections

from urllib.parse import quote


class BindingsExtractor(abc.ABC, collections.UserDict):
    """Binding Representation for an ELTeC resource."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize a BindingExtractor object."""
        self.data = self.generate_bindings()

    @abc.abstractmethod
    def generate_bindings(self) -> dict:
        raise NotImplementedError

    def _quote_iri(self, url: str) -> str:
        """Parse and ascii quote IRIs for processing."""
        parts = url.split("/")
        path = parts.pop()
        parts.append(quote(path))

        quoted_iri = "/".join(parts)

        return quoted_iri
