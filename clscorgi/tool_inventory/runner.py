"""Runner for Tool Inventory table to RDF conversion."""

from clscorgi.vocabs.vocabs_utils import pull_remote_vocabs


def tool_inventory_runner() -> None:
    """Tool Inventory runner.

    Generate triples and serialize to output/tool_inventory/.
    """
    pull_remote_vocabs()
