from collections.abc import Sequence
from typing import Callable, Mapping

from d100.ast.dice import ASTDice as ASTDice
from d100.ast.die import DiceSize as DiceSize, Die as Die
from .node import ASTNode as ASTNode, Number as Number
from .operators import BinaryOperator as BinaryOperator
from ..context import RollContext as RollContext
from ..distribution import Distribution as Distribution
from ..errors import RollError as RollError, RollValueError as RollValueError

class BinOp(Number):
    """BinOps are operations done on two children."""

    op: BinaryOperator
    left: Number
    right: Number
    BINARY_OPS: Mapping[BinaryOperator, Callable[[int | float, int | float], int | float]]
    def __init__(self, left: Number, op: BinaryOperator, right: Number, ast: ASTNode) -> None: ...
    @property
    def total(self) -> int: ...
    @property
    def children(self) -> Sequence[Number]: ...
    def copy(self) -> BinOp: ...
    def extract_dice(self) -> Sequence[Die]: ...

class ASTBinOp(ASTNode):
    """BinOps are operations done on two children."""

    op: BinaryOperator
    left: ASTNode
    right: ASTNode
    def __init__(self, left: ASTNode, op: BinaryOperator, right: ASTNode) -> None: ...
    @property
    def children(self) -> Sequence[ASTNode]: ...
    def copy(self) -> ASTBinOp: ...
    def roll(self, context: RollContext) -> tuple[BinOp, Sequence[BinOp]]: ...
    DISTRIBUTION_OPS: Mapping[BinaryOperator, Callable[[Distribution, Distribution], Distribution]]
    def distribution(self) -> Distribution: ...
    @property
    def is_comparison(self) -> bool: ...
    def find_dice(self, count: int, size: DiceSize) -> ASTDice | None: ...
