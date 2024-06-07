"""Runner for Postdata extraction."""


from collections.abc import Iterator
from importlib.resources import files
from itertools import count, islice
from pathlib import Path

from clisn import CLSInfraNamespaceManager
from clscorgi.postdata.triple_extractor import \
    get_clscor_relevant_triples_from_graph
from lodkit import _Triple
from more_itertools import ichunked
from rdflib import Graph


def chunk_post_data_files() -> Iterator[Iterator]:
    """Produce chunks of """
    def _postdata_ttl_files():
        for f in files("clscorgi.postdata.data").iterdir():
            if f.name.endswith(".ttl"):
                yield f

    yield from ichunked(_postdata_ttl_files(), 200)


def generate_triples_from_chunk(chunk: Iterator[Path]) -> Iterator[_Triple]:
    for path in chunk:
        graph = Graph().parse(path)
        yield from get_clscor_relevant_triples_from_graph(graph)


def generate_graph_from_chunk(chunk: Iterator[Path]) -> Graph:
    graph = Graph()
    CLSInfraNamespaceManager(graph)

    print("INFO: Generating triples...")

    for triple in generate_triples_from_chunk(chunk):
        graph.add(triple)

    return graph


def postdata_runner() -> None:
    output_dir = files("clscorgi.output.postdata")
    cnt = count()

    chunks = islice(chunk_post_data_files(), 5)
    for chunk in chunks:
        graph = generate_graph_from_chunk(chunk)
        file_name = output_dir / f"postdata_{next(cnt)}.ttl"
        print(f"INFO: Materializing triples in {file_name.name}.")

        with open(file_name, "w") as f:
            f.write(graph.serialize())


if __name__ == "__main__":
    postdata_runner()
