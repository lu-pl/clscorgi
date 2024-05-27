"""XML tree extractors for the DLK corpus."""

import re
from collections.abc import Iterator
from functools import partial

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
        surname = TEIXPath("tei:persName/tei:surname/text()")(element)[0]
        forename = TEIXPath("tei:persName/tei:forename/text()")(element)[0]

        names = {
            "forename": forename,
            "surname": surname,
            "full_name": f"{forename} {surname}"
        }

        yield names


def get_title(tree: etree._ElementTree) -> str:
    """Extract title from a DLK tree."""
    try:
        title = TEIXPath("//tei:titleStmt/tei:title/text()")(tree)[0]
        title = title.strip()

        if re.search(r"N\.A\.", title):
            title = None
    except IndexError:
        title = None
    return title


def get_first_line(tree: etree._ElementTree) -> str:
    """Extract the first line text from a DLK tree."""
    first_line = TEIXPath("//tei:lg[@type='poem']/tei:lg/tei:l[1]/text()")(tree)[0]
    first_line = first_line.strip(", ")
    return first_line


def get_urn(tree: etree._ElementTree) -> str:
    """Extract URN from a DLK tree."""
    urn = TEIXPath("//tei:sourceDesc/tei:p/@corresp")(tree)[0]
    return urn



##################################################
from urllib.request import urlretrieve

test_url = "https://raw.githubusercontent.com/tnhaider/DLK/master/DLK/tei/tei_plain/dta.poem.1-Ebeling%2C_Johann_Justus-N.A..tei.xml"
_temp_file_name, _ = urlretrieve(test_url)

with open(_temp_file_name) as f:
    tree = etree.parse(f)
