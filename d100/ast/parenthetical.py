from collections.abc import Sequence
from typing import get_args

from ..errors import RollError

from .operators import AdvantageCategory, Operator

from .dice import ASTDice, find_from_advantage
from .die import DiceSize, Die
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

    def extract_dice(self) -> Sequence[Die]:
        return self.value.extract_dice()


class ASTParenthetical(ASTNode):
    """Expressions are usually the root of all ASTs."""

    value: ASTNode
    operator: Operator | None

    def __init__(self, value: ASTNode, operator: Operator | None) -> None:
        if operator and operator.op not in get_args(AdvantageCategory):
            raise RollError(f"Parenthetical expressions only support advantage operators.")

        self.value = value
        self.operator = operator

    def copy(self) -> "ASTParenthetical":
        operator = self.operator.copy() if self.operator else None
        return ASTParenthetical(self.value.copy(), operator)

    @property
    def children(self) -> Sequence[ASTNode]:
        return [self.value]

    def __str__(self) -> str:
        return f"({str(self.value)})"

    def roll(self, context: RollContext) -> tuple[Parenthetical, Sequence[Parenthetical]]:
        if self.operator:
            advantage = self.operator.op
            roll_count = self.operator.sels[0].num
        else:
            advantage = None
            roll_count = 1

        all_values: list[Number] = []
        possible_results: list[Number] = []

        for _ in range(roll_count):
            value, values = self.value.roll(context)
            assert value in values

            all_values.extend(values)
            possible_results.append(value)

        result = find_from_advantage(possible_results, advantage)

        parentheticals = [Parenthetical(val, self) for val in all_values]
        parenthetical = parentheticals[all_values.index(result)]

        return parenthetical, parentheticals

    def distribution(self) -> Distribution:
        return self.value.distribution()

    @property
    def is_comparison(self) -> bool:
        return self.value.is_comparison

    def find_dice(self, count: int, size: DiceSize) -> ASTDice | None:
        return self.value.find_dice(count, size)
