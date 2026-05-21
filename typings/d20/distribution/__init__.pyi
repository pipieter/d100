from .. import diceast as ast
from .calculate import ConvolutionDistributionBuilder, DiscreteDistributionBuilder
from .distribution import Distribution

class DistributionBuilder:
    def build(self, expr: ast.Node) -> Distribution:
        """Parse a distribution from a d20 ast node.
        Args:
            ast (ast.Node): The node to be parsed.

        Raises:
            DiceParseError: When an unsupported node is parsed.

        Returns:
            Distribution: The distribution matching the node.
        """
        ...
    


