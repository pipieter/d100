from collections.abc import Sequence

from .node import ASTNode, Number
from ..context import RollContext
from ..distribution import Distribution


class Parenthetical(Number):
    """Parentheticals contain values between parentheses."""

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
        return f"<Parenthetical value={repr(self.value)} />"

    def copy(self) -> Number:
        return Parenthetical(self.value.copy(), self.ast)


class ASTParenthetical(ASTNode):
    """Expressions are usually the root of all ASTs."""

    value: ASTNode

    def __init__(self, value: ASTNode) -> None:
        self.value = value

    def copy(self) -> "ASTParenthetical":
        return ASTParenthetical(self.value.copy())

    @property
    def children(self) -> Sequence[ASTNode]:
        return [self.value]

    def __str__(self) -> str:
        return f"({str(self.value)})"

    def roll(self, context: RollContext) -> tuple[Parenthetical, Sequence[Parenthetical]]:
        value, values = self.value.roll(context)
        assert value in values

        parentheticals = [Parenthetical(val, self) for val in values]
        parenthetical = parentheticals[values.index(value)]

        return parenthetical, parentheticals

    def distribution(self) -> Distribution:
        return self.value.distribution()
