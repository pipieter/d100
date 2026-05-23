from collections.abc import Sequence

from d100.ast.die import Die

from .node import ASTNode, Number
from ..context import RollContext
from ..distribution import Distribution


class Expression(Number):
    """Expressions are usually the root of all Number trees."""

    value: Number

    def __init__(self, value: Number, ast: ASTNode) -> None:
        super().__init__(ast)
        self.value = value

    @property
    def total(self) -> int:
        return self.value.total

    @property
    def children(self) -> Sequence[Number]:
        return [self.value]

    def __repr__(self) -> str:
        return f"<Expression value={repr(self.value)} />"

    def copy(self) -> Number:
        return Expression(self.value.copy(), self.ast)

    def extract_dice(self) -> Sequence[Die]:
        return self.value.extract_dice()


class ASTExpression(ASTNode):
    """Expressions are usually the root of all ASTs."""

    value: ASTNode

    def __init__(self, value: ASTNode) -> None:
        self.value = value

    def copy(self) -> "ASTExpression":
        return ASTExpression(self.value.copy())

    @property
    def children(self) -> Sequence[ASTNode]:
        return [self.value]

    def __str__(self) -> str:
        return str(self.value)

    def roll(self, context: RollContext) -> tuple[Expression, Sequence[Expression]]:
        value, values = self.value.roll(context)
        assert value in values

        expressions = [Expression(val, self) for val in values]
        expression = expressions[values.index(value)]
        return expression, expressions

    def distribution(self) -> Distribution:
        return self.value.distribution()

    @property
    def is_comparison(self) -> bool:
        return self.value.is_comparison
