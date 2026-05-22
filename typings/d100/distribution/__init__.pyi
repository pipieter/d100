from .calculate import ConvolutionDistributionBuilder, DiscreteDistributionBuilder
from .distribution import Distribution
from .. import diceast as ast

class DistributionBuilder:
    def build(self, expr: ast.Node) -> Distribution:
        """Parse a distribution from a ast node.
        Args:
            ast (ast.Node): The node to be parsed.

        Raises:
            DiceParseError: When an unsupported node is parsed.

        Returns:
            Distribution: The distribution matching the node.
        """
        ...
