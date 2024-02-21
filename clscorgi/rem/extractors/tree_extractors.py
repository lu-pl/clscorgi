"""Tree/XPath exractor functions"""

from collections.abc import Callable, Sequence
from functools import partial
from importlib.resources import files
from pathlib import Path
from typing import Any

from lxml import etree
from clscorgi.utils.utils import first


TEIXPath = partial(
    etree.XPath,
    namespaces={
        "tei": "http://www.tei-c.org/ns/1.0"
    }
)

def xpath_factory(xpath: str) -> Callable[[etree._ElementTree], Any]:
    def _wrapper(tree: etree._ElementTree):
        result = TEIXPath(xpath)(tree)
        return first(result)
    return _wrapper


def get_publication(tree: etree._ElementTree) -> dict:
    _publication_stmt = first(TEIXPath("//tei:publicationStmt")(tree))
    idno = first(TEIXPath("tei:idno/text()")(_publication_stmt))
    date = first(TEIXPath("tei:date/@when")(_publication_stmt))

    return {
        "idno": idno,
        "date": date
    }

def get_source(tree: etree._ElementTree) -> dict:
    _ms_desc = first(TEIXPath("//tei:sourceDesc/tei:msDesc")(tree))
    _ms_identifier = first(TEIXPath("tei:msIdentifier")(_ms_desc))
    _history = first(TEIXPath("tei:history/tei:origin")(_ms_desc))

    msname = first(TEIXPath("tei:msName/text()")(_ms_identifier))
    repo = first(TEIXPath("tei:altIdentifier/tei:repository/text()")(_ms_identifier))
    idno = first(TEIXPath("tei:altIdentifier/tei:idno/text()")(_ms_identifier))

    object_type = first(TEIXPath("tei:objectType/text()")(_history))
    census_link = first(TEIXPath("//tei:recordHist/tei:source/tei:ref/@target")(tree))

    tpq = first(TEIXPath("tei:origDate/@notBefore-custom")(_history))
    taq = first(TEIXPath("tei:origDate/@notAfter-custom")(_history))

    return {
        "msname": msname,
        "repo": repo,
        "idno": idno,

        "object_type": object_type,
        "census_link": census_link,

        "tpq": tpq,
        "taq": taq
    }


get_id = xpath_factory("//tei:fileDesc/@xml:id")
get_title = xpath_factory("//tei:titleStmt/tei:title/text()")
get_genre = xpath_factory("//tei:teiHeader/@style")
get_token = xpath_factory("//tei:fileDesc/tei:extent[@type='Tokens']/text()")

test_dir = files("clscorgi.rem.data.headers")
test_file = test_dir / "M001.xml"
test_tree = etree.parse(test_file)
