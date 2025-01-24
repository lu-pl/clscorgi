"""Runner for Tool Inventory table to RDF conversion."""

from importlib.resources import files

from clscorgi.tool_inventory.triple_generators import generate_tool_inventory_graph
from clscorgi.vocabs.vocabs_utils import pull_remote_vocabs


def tool_inventory_runner(pull_vocabs: bool = False) -> None:
    """Tool Inventory runner.

    Generate triples and serialize to output/tool_inventory/.
    """
    if pull_vocabs:
        pull_remote_vocabs()

    output_file = files("clscorgi.output.tool_inventory") / "tool_intenventory.ttl"
    graph = generate_tool_inventory_graph()

    with open(str(output_file), "w") as f:
        f.write(graph.serialize())
