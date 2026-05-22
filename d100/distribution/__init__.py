from .calculate import ConvolutionDistributionBuilder, DiscreteDistributionBuilder
from .distribution import Distribution
from .. import diceast as ast


class DistributionBuilder:
    def _parse_dimensions(self, count: int, sides: str | int) -> tuple[int, int]:
        """Parse the dimensions from a dice

        Args:
            count (int): The count of the dice.
            sides (str | int): The sides of the dice.

        Returns:
            tuple[int, int]: The parsed values packed as a tuple, representing the count and sides respectively.
        """
        if sides == "%":
            sides = 100
        else:
            sides = int(sides)
        return count, sides

    def build(self, expr: ast.Node) -> Distribution:
        """Parse a distribution from a d20 ast node.
        Args:
            ast (ast.Node): The node to be parsed.

        Raises:
            DiceParseError: When an unsupported node is parsed.

        Returns:
            Distribution: The distribution matching the node.
        """

        if isinstance(expr, ast.Expression):
            return self.build(expr.roll)  # type: ignore

        if isinstance(expr, ast.Literal):
            return Distribution({expr.value: 1.0})  # type: ignore

        if isinstance(expr, ast.UnOp):
            if expr.op == "-":
                return -self.build(expr.value)  # type: ignore
            if expr.op == "+":
                return self.build(expr.value)  # type: ignore
            raise SyntaxError(f"Unsupported UnOp operator '{expr.op}'.")

        if isinstance(expr, ast.BinOp):
            if expr.op == "+":
                return self.build(expr.left) + self.build(expr.right)
            if expr.op == "-":
                return self.build(expr.left) - self.build(expr.right)
            if expr.op == "*":
                return self.build(expr.left) * self.build(expr.right)
            if expr.op == "/":
                return self.build(expr.left) // self.build(expr.right)
            if expr.op == ">":
                return self.build(expr.left) > self.build(expr.right)
            if expr.op == ">=":
                return self.build(expr.left) >= self.build(expr.right)
            if expr.op == "<":
                return self.build(expr.left) < self.build(expr.right)
            if expr.op == "<=":
                return self.build(expr.left) <= self.build(expr.right)
            if expr.op == "==":
                return self.build(expr.left).equals(self.build(expr.right))
            if expr.op == "!=":
                return self.build(expr.left).not_equals(self.build(expr.right))

            raise SyntaxError(f"Unsupported BinOp operator '{expr.op}'.")

        if isinstance(expr, ast.Parenthetical):
            return self.build(expr.value)

        if isinstance(expr, ast.Dice):
            count, sides = self._parse_dimensions(expr.num, expr.size)
            operations = expr.operations

            contains_non_convolution_operation = any(
                not ConvolutionDistributionBuilder.supports_operation(op) for op in operations
            )

            if contains_non_convolution_operation:
                builder = DiscreteDistributionBuilder(count, sides, operations)
            else:
                builder = ConvolutionDistributionBuilder(count, sides, operations)

            return builder.distribution()

        raise SyntaxError(f"Unsupported node type '{type(expr)}'.")
