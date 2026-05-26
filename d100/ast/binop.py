import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Callable, Mapping

from .dice import ASTDice
from .die import Die
from .node import ASTNode, Number
from .operators import BinaryOperator
from ..context import RollContext
from ..distribution import Distribution
from ..errors import RollError, RollValueError

if TYPE_CHECKING:
    from .die import DiceSize
else:
    DiceSize = Any


class BinOp(Number):
    """BinOps are operations done on two children."""

    op: BinaryOperator
    left: Number
    right: Number

    BINARY_OPS: Mapping[BinaryOperator, Callable[[int | float, int | float], int | float]] = {
        "+": lambda l, r: l + r,
        "-": lambda l, r: l - r,
        "*": lambda l, r: l * r,
        "/": lambda l, r: l / r,
        "//": lambda l, r: l // r,
        "%": lambda l, r: l % r,
        "<": lambda l, r: int(l < r),
        ">": lambda l, r: int(l > r),
        ">=": lambda l, r: int(l >= r),
        "<=": lambda l, r: int(l <= r),
        "==": lambda l, r: int(l == r),
        "!=": lambda l, r: int(l != r),
    }

    def __init__(self, left: Number, op: BinaryOperator, right: Number, ast: ASTNode) -> None:
        super().__init__(ast)
        self.op = op
        self.left = left
        self.right = right

    @property
    def total(self) -> int:
        try:
            result = self.BINARY_OPS[self.op](self.left.total, self.right.total)
            return math.floor(result)
        except ZeroDivisionError:
            raise RollValueError("Cannot divide by zero.")

    @property
    def children(self) -> Sequence[Number]:
        return [self.left, self.right]

    def __repr__(self) -> str:
        return f"<BinOp op={self.op} left={repr(self.left)} right={repr(self.right)} />"

    def copy(self) -> "BinOp":
        return BinOp(self.left.copy(), self.op, self.right.copy(), self.ast)

    def extract_dice(self) -> Sequence[Die]:
        return list(self.left.extract_dice()) + list(self.right.extract_dice())


class ASTBinOp(ASTNode):
    """BinOps are operations done on two children."""

    op: BinaryOperator
    left: ASTNode
    right: ASTNode

    def __init__(self, left: ASTNode, op: BinaryOperator, right: ASTNode) -> None:
        self.op = op
        self.left = left
        self.right = right

    @property
    def children(self) -> Sequence[ASTNode]:
        return [self.left, self.right]

    def __str__(self):
        return f"{str(self.left)} {self.op} {str(self.right)}"

    def copy(self) -> "ASTBinOp":
        return ASTBinOp(self.left.copy(), self.op, self.right.copy())

    def roll(self, context: RollContext) -> tuple[BinOp, Sequence[BinOp]]:
        left_value, left_values = self.left.roll(context)
        right_value, right_values = self.right.roll(context)

        assert left_value in left_values
        assert right_value in right_values

        binops: list[BinOp] = []

        binop = None
        for lval in left_values:
            for rval in right_values:
                value = BinOp(lval, self.op, rval, self)
                binops.append(value)
                if lval is left_value and rval is right_value:
                    binop = value

        # Should never occur if every other function is implemented correctly, but this is required for the linter
        if binop is None:
            raise RollError("Could not construct roller binop")

        return binop, binops

    DISTRIBUTION_OPS: Mapping[BinaryOperator, Callable[[Distribution, Distribution], Distribution]] = {
        "+": lambda l, r: l + r,
        "-": lambda l, r: l - r,
        "*": lambda l, r: l * r,
        "/": lambda l, r: l // r,
        "//": lambda l, r: l // r,
        "%": lambda l, r: l % r,
        "<": lambda l, r: (l < r),
        ">": lambda l, r: (l > r),
        ">=": lambda l, r: (l >= r),
        "<=": lambda l, r: (l <= r),
        "==": lambda l, r: l.equals(r),
        "!=": lambda l, r: l.not_equals(r),
    }

    def distribution(self) -> Distribution:
        return self.DISTRIBUTION_OPS[self.op](self.left.distribution(), self.right.distribution())

    @property
    def is_comparison(self) -> bool:
        return self.op in {">", "<", ">=", "<=", "==", "!="}

    def find_dice(self, count: int, size: DiceSize) -> ASTDice | None:
        if self.op not in ["-", "+"]:
            return None

        left = self.left.find_dice(count, size)
        if left is not None:
            return left

        right = self.right.find_dice(count, size)
        if right is not None:
            return right

        return None
