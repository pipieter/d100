import math
from collections.abc import Sequence
from typing import Union

from .node import ASTNode, Number
from ..context import RollContext
from ..distribution import Distribution

LiteralValue = Union[int, float]


class Literal(Number):
    """Literals are literal numeric values."""

    value: int

    def __init__(self, value: int, ast: ASTNode) -> None:
        super().__init__(ast)
        self.value = value

    @property
    def total(self) -> int:
        return self.value

    @property
    def children(self) -> Sequence[Number]:
        return []

    def __repr__(self) -> str:
        return f"<Literal value={self.value} />"

    def copy(self) -> "Literal":
        return Literal(self.value, self.ast)


class ASTLiteral(ASTNode):
    """Literals are literal numeric values."""

    value: int | float

    def __init__(self, value: int | float) -> None:
        self.value = value

    @property
    def children(self) -> Sequence[ASTNode]:
        return []

    def __str__(self) -> str:
        return str(self.value)

    def copy(self) -> "ASTLiteral":
        return ASTLiteral(self.value)

    def _calculated_value(self, round_down: bool) -> int:
        if round_down:
            return math.floor(self.value)
        else:
            return math.ceil(self.value)

    def roll(self, context: RollContext) -> tuple[Literal, Sequence[Literal]]:
        value = self._calculated_value(round_down=True)
        literal = Literal(value, self)
        return literal, [literal]

    def distribution(self) -> Distribution:
        value = self._calculated_value(round_down=True)
        return Distribution({value: 1.0})
