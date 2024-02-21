"""ABC for binding generators."""

import abc
import collections


class BindingsExtractor(abc.ABC, collections.UserDict):
    """Binding Representation for an ELTeC resource."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize a BindingExtractor object."""
        self.data = self.generate_bindings()

    @abc.abstractmethod
    def generate_bindings(self) -> dict:
        raise NotImplementedError
