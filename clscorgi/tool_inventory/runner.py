"""Runner for Tool Inventory table to RDF conversion."""

from importlib.resources import files
import logging

from clscorgi.tool_inventory.triple_generators import generate_tool_inventory_graph
from clscorgi.utils.reasoning.reasoner import run_reasoner
from clscorgi.vocabs.vocabs_utils import pull_remote_vocabs


logger = logging.getLogger(__name__)


def tool_inventory_runner(pull_vocabs: bool = False, generate_inferred=False) -> None:
    """Tool Inventory runner.

    Generate triples and serialize to output/tool_inventory/.
    """
    if pull_vocabs:
        logger.info("Pulling remote vocabs.")
        pull_remote_vocabs()

    _output_path = files("clscorgi.output.tool_inventory")

    output_file = _output_path / "tool_inventory.ttl"
    graph = generate_tool_inventory_graph()

    with open(str(output_file), "w") as f:
        logger.info("Serializing graph to output file '%s'.", output_file)
        f.write(graph.serialize())

    if generate_inferred:
        logger.info("Running reasoner.")
        graph = run_reasoner(graph)

        output_file_inferred = _output_path / "tool_inventory_inferred.ttl"

        with open(str(output_file_inferred), "w") as f:
            logger.info(
                "Serializing inferred graph to output file '%s'.", output_file_inferred
            )
            f.write(graph.serialize())


tool_inventory_runner(generate_inferred=True)
