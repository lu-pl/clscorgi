"""Runner for Tool Inventory table to RDF conversion."""

from importlib.resources import files

from clscorgi.vocabs.vocabs_utils import pull_remote_vocabs


def tool_inventory_runner() -> None:
    """Tool Inventory runner.

    Generate triples and serialize to output/tool_inventory/.
    """
    pull_remote_vocabs()

    # output_dir = files("clscorgi.output.tool_inventory")
    # with open(output_dir / "tool_inventory.ttl", "w") as f:
    #     f.write(graph.serialize())
