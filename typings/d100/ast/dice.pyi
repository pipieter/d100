from collections.abc import Sequence
from typing import TypeVar

from lark import Token as Token

from .die import DiceSize as DiceSize, Die as Die
from .node import ASTNode as ASTNode, Number as Number
from .operators import (
    AdvantageCategory as AdvantageCategory,
    Operator as Operator,
    OperatorCategory as OperatorCategory,
    Selector as Selector,
)
from ..context import RollContext as RollContext
from ..distribution import (
    ConvolutionDistributionBuilder as ConvolutionDistributionBuilder,
    DiscreteDistributionBuilder as DiscreteDistributionBuilder,
    Distribution as Distribution,
)
from ..errors import RollError as RollError, RollValueError as RollValueError

TNumber = TypeVar("TNumber", bound=Number)

def find_from_advantage(rolls: Sequence[TNumber], adv: OperatorCategory | None) -> TNumber: ...

class Dice(Number):
    """Represents a set of dice."""

    dice: list[Die]
    count: int
    size: DiceSize
    operators: list["Operator"]
    def __init__(
        self,
        dice: list[Die],
        count: int,
        size: DiceSize,
        operators: list["Operator"],
        ast: ASTNode,
        context: RollContext,
    ) -> None: ...
    @classmethod
    def new(cls, ast: ASTDice, context: RollContext) -> tuple["Dice", list["Dice"]]:
        """Roll a new set of dice."""
    @property
    def keptset(self) -> Sequence[Die]:
        """Return a list of all dice that were not dropped."""
    @property
    def total(self) -> int: ...
    @property
    def children(self) -> Sequence[Number]: ...
    def roll_another(self, negative: bool = False) -> None:
        """Roll another die and add it to the dice set."""
    def copy(self) -> Dice: ...
    def extract_dice(self) -> Sequence[Die]: ...
    def select(self, selector: Selector) -> set[Die]: ...
    def operate(self, operator: Operator) -> None:
        """Apply an operator to the dice set."""
    def keep(self, selector: Selector) -> None: ...
    def drop(self, selector: Selector) -> None: ...
    def reroll(self, selector: Selector) -> None: ...
    def reroll_once(self, selector: Selector) -> None: ...
    def explode(self, selector: Selector) -> None: ...
    def explode_once(self, selector: Selector) -> None: ...
    def reroll_and_subtract(self, selector: Selector) -> None: ...
    def explode_red(self, selector: Selector) -> None: ...
    def minimum(self, selector: Selector) -> None: ...
    def maximum(self, selector: Selector) -> None: ...

class ASTDice(ASTNode):
    """A dice is a collection of die with or without operators."""

    num: int
    size: DiceSize
    operations: list[Operator]
    def __init__(self, num: int | Token, size: int | str | Token, *operations: Operator) -> None: ...
    @property
    def children(self) -> Sequence[ASTNode]: ...
    def copy(self) -> ASTDice: ...
    def roll(self, context: RollContext) -> tuple[Dice, list[Dice]]: ...
    def distribution(self) -> Distribution: ...
    @property
    def is_comparison(self) -> bool: ...
    def find_dice(self, count: int, size: DiceSize) -> ASTDice | None: ...
