"""Experimental URINamespace constructor. This is a possible candidate for LODKit."""

import re

from rdflib import Namespace, URIRef
from lodkit import mkuri_factory


def NamespaceMetaFactory(namespace: Namespace | str) -> type:
    """Factory for creating a URINamespace Metaclass."""
    _namespace = (
        Namespace(namespace)
        if isinstance(namespace, str)
        else namespace
    )

    mkuri = mkuri_factory(_namespace)

    class AutoDict(dict):
        """Dict subclass that generates a URI for missing keys.

        This is intended to be used in the __prepare__ namespace hook
        for resolving missing attributes with a URI constructor.
        """
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(self, *args, **kwargs)

        def __missing__(self, key) -> URIRef:
            self[key] = uri = mkuri()
            return uri


    class MetaURINamespace(type):
        """URINamespace Metaclass.

        Resolves class attributes with a URI constructor.
        The behavior is inspired by dataclasses and the like.
        """
        def __new__(mcls, name, bases, cls_dict):

            for key, value in cls_dict.items():
                if (re.match(r"^__.+__$", key) is None) and isinstance(value, str):
                    cls_dict.update({key: mkuri(value)})

            return super().__new__(mcls, name, bases, cls_dict)

        @classmethod
        def __prepare__(mcls, name, bases, **kwargs) -> dict:
            return AutoDict()

    return MetaURINamespace


def nsbase(namespace: str | Namespace) -> type:
    """Base class constructor for a URINamespace.

    Returns a URINamespace class with a pre-loaded metaclass.
    The intended use for this is to have dataclass like behavior
    where missing class attributes are resolved with a URI constructor:

    class namespace(uri("https://some.namespace/test/)):
        some_uri
        another_uri="hash value"

    namespace.some_uri     #  https://some.namespace/test/<uuid>
    namespace.another_uri  #  https://some.namespace/test/<hash 'hash value'>)
    """
    class URINamespace(metaclass=NamespaceMetaFactory(namespace)):
        pass
    return URINamespace
