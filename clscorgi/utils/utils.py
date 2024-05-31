"""Miscellaneous utilies for clscorgi."""

import contextlib
import functools
import hashlib
import html
import inspect
import re
from collections.abc import Callable, Mapping, Sequence
from types import SimpleNamespace
from typing import Any, TypeVar
from uuid import uuid4

from lodkit.utils import genhash
from rdflib import URIRef

T = TypeVar("T")
TDefault = TypeVar("TDefault")


def resolve_source_type(source_type: str, join_value=" ") -> str:
    """Resolve source_type data for vocabs lookup.

    Split a camelCase string and join it using join_value.
    """
    resolved = functools.reduce(
        lambda x, y: f"{x.lower()}{join_value}" + y.lower(),
        re.split('(?<=[a-z])(?=[A-Z])', source_type)
    )

    return resolved


def first(seq: Sequence[T],
          default: TDefault | None = None) -> T | TDefault | None:
    """Try to return the first item of a Sequence.

    If index lookup fails, return a default value.
    """
    with contextlib.suppress(Exception):
        return seq[0]
    return default


def trim(string: str) -> str:
    """Remove leading, trailing and generally superfluous whitespace."""
    trimmed = re.sub(r"\s{2,}", " ", string).strip()
    return trimmed


def _or(*operands: Callable[..., T],
        args: tuple = (),
        kwargs: dict | None = None
        ) -> T | None:
    """Logical n-ary OR.

    Evaluates a series of callables (operands) with
    args and kwargs and short-circuits on first truthy result.
    """
    kwargs = {} if kwargs is None else kwargs

    for operand in operands:
        if result := operand(*args, **kwargs):
            return result
    return None


def mkuri(
        hash_value: str | None = None,
        length: int | None = 10,
        hash_function: Callable = hashlib.sha256
) -> URIRef:
    """Create a CLSCor entity URI.

    If a hash value is give, the path is generated using
    a hash function, else the path is generated using a uuid4.
    """
    _base_uri: str = "https://clscor.io/entity/"
    _path: str = (
        str(uuid4()) if hash_value is None
        else genhash(
                hash_value,
                length=length,
                hash_function=hash_function
        )
    )

    return URIRef(f"{_base_uri}{_path[:length]}")


def uri_ns(*names: str | tuple[str, str]) -> SimpleNamespace:
    """Generate a Namespace mapping for names and computed URIs."""
    def _uris():
        for name in names:
            match name:
                case str():
                    yield name, mkuri()
                case tuple():
                    yield name[0], mkuri(name[1])
                case _:
                    raise Exception(
                        "Args must be of type str | tuple[str, str]."
                    )

    return SimpleNamespace(**dict(_uris()))


def get_e39_hash_value(data: list[dict]):
    """Get a hash value for e39 assertions from author IDs.

    Select the first id_value that has an id_type,
    else return the first id_value.
    """
    for element in data:
        if element["id_type"]:
            return element["id_value"]

    return data[0]["id_value"]


def revalmap(f: Callable, d: Mapping) -> dict:
    """Recursively apply a callable to mapping values."""
    return {
        key: f(value)
        if not isinstance(value, Mapping)
        else revalmap(f, value)
        for key, value
        in d.items()
    }


def require_defaults(
        _f: Callable | None = None,
        check: Callable[[Any], bool] = bool,
        fail_factory: Callable[[Any], Any] = lambda x: tuple()
):
    """Skip decorator.

    The decorator inspects default arguments of the decorated function
    and runs values against the check predicate.
    If the predicate returns False for any value,
    the result of calling fail_factory is returned;
    else the decorator returns the decorated function.
    """
    def _decor(f: Callable):
        @functools.wraps(f)
        def _wrapper(*args, **kwargs):
            for parameter in inspect.signature(f).parameters.values():
                if (default := parameter.default) is not inspect._empty:
                    if not check(default):
                        return fail_factory(default)
            return f(*args, **kwargs)
        return _wrapper

    if _f is None:
        return _decor
    return _decor(_f)


def unescape(string: str) -> str:
    """Double unescape XML/HTML encoded strings."""
    return html.escape(html.escape(string))
