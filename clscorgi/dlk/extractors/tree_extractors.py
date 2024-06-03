"""XML tree extractors for the DLK corpus."""

import re
from collections.abc import Callable, Iterator
from functools import partial

from clscorgi.utils.utils import (construct_artificial_title, unescape,
                                  unescaped)
from lxml import etree

TEIXPath = partial(
    etree.XPath,
    namespaces={
        "tei": "http://www.tei-c.org/ns/1.0"
    }
)


def get_features(tree: etree._ElementTree) -> dict:
    """Extract the linguistic feature counts from a DLK tree."""
    xpath_result = TEIXPath("//tei:extent")(tree)

    features = {
        element.xpath("@type")[0]: element.text
        for element in xpath_result[0]
    }

    return features


def get_author_names(tree: etree._ElementTree) -> Iterator[dict]:
    """Extract author names from a DLK tree."""
    xpath_result = TEIXPath("//tei:author")(tree)

    for element in xpath_result:
        surname = unescape(TEIXPath("tei:persName/tei:surname/text()")(element)[0])
        forename = unescape(TEIXPath("tei:persName/tei:forename/text()")(element)[0])

        names = {
            "forename": forename,
            "surname": surname,
            "full_name": f"{forename} {surname}"
        }

        yield names


@unescaped
def get_title(tree: etree._ElementTree) -> str | None:
    """Extract title from a DLK tree."""
    try:
        title = TEIXPath("//tei:titleStmt/tei:title/text()")(tree)[0]
        title = title.strip()

        if re.search(r"N\.A\.", title):
            title = None
    except IndexError:
        title = None

    return title


@unescaped
def get_artificial_title(tree: etree._ElementTree) -> str:
    """Extract the first line text from a DLK tree and construt a title."""
    first_line = TEIXPath("//tei:lg[@type='poem']/tei:lg/tei:l[1]/text()")(tree)[0]
    artificial_title = construct_artificial_title(first_line.strip(","))
    return artificial_title


def get_urn(tree: etree._ElementTree) -> str:
    """Extract URN from a DLK tree."""
    urn = TEIXPath("//tei:sourceDesc/tei:p/@corresp")(tree)[0]
    return urn


def get_publication_date(tree: etree._ElementTree) -> str:
    """Extract the publication date from a DLK tree."""
    xpath: str = "//tei:publicationStmt/tei:date[@type='publication']/text()"
    date: str = TEIXPath(xpath)(tree)[0]
    return date

##################################################
