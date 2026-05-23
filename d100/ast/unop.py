from collections.abc import Sequence

from .dice import ASTDice
from .die import DiceSize, Die
from .node import ASTNode, Number
from .operators import UnaryOperator
from ..context import RollContext
from ..distribution import Distribution


class UnOp(Number):
    """UnOps are numbers modified by a unary operator."""

    op: UnaryOperator
    value: Number

    def __init__(self, op: UnaryOperator, value: Number, ast: ASTNode) -> None:
        super().__init__(ast)
        self.op = op
        self.value = value

    @property
    def total(self) -> int:
        match self.op:
            case "+":
                return self.value.total
            case "-":
                return -self.value.total

    @property
    def children(self) -> Sequence[Number]:
        return [self.value]

    def __repr__(self) -> str:
        return f"<UnOp op={self.op} value={repr(self.value)} />"

    def copy(self) -> Number:
        return UnOp(self.op, self.value.copy(), self.ast)

    def extract_dice(self) -> Sequence[Die]:
        return self.value.extract_dice()


class ASTUnOp(ASTNode):
    """UnOps are nodes modified by a unary operator."""

    op: UnaryOperator
    value: ASTNode

    def __init__(self, op: UnaryOperator, value: ASTNode) -> None:
        self.op = op
        self.value = value

    @property
    def children(self) -> Sequence[ASTNode]:
        return [self.value]

    def __str__(self) -> str:
        return f"{self.op}{self.value}"

    def copy(self) -> "ASTUnOp":
        return ASTUnOp(self.op, self.value.copy())

    def roll(self, context: RollContext) -> tuple[UnOp, Sequence[UnOp]]:
        value, values = self.value.roll(context)
        assert value in values

        unops = [UnOp(self.op, val, self) for val in values]
        unop = unops[values.index(value)]

        return unop, unops

    def distribution(self) -> Distribution:
        distribution = self.value.distribution()

        match self.op:
            case "+":
                return distribution
            case "-":
                return -distribution

    @property
    def is_comparison(self) -> bool:
        return False

    def find_dice(self, count: int, size: DiceSize) -> ASTDice | None:
        return self.value.find_dice(count, size)
