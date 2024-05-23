"""Link extractor for the DLK repo."""

import os

from collections.abc import Callable, Iterator
from functools import partial

from github import Github, Auth
from dotenv import load_dotenv


load_dotenv()
token = os.getenv("TOKEN")
auth = Auth.Token(token)

g = Github(auth=auth)

def _get_raw_links(repository: str) -> Iterator[str]:
    """Get raw XML file links from level1 of an ELTeC repo."""
    repo = g.get_repo(repository)
    contents = repo.get_contents("DLK/tei/tei_plain")

    for content in contents:
        yield (
            "https://raw.githubusercontent.com/tnhaider/DLK/master/DLK/tei/tei_plain/"
            f"{content.name}"
        )


get_dlk_raw_links: Callable[[], Iterator] = partial(_get_raw_links, "tnhaider/DLK")
