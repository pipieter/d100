from collections.abc import Sequence
from typing import Callable, Mapping, TypeVar

from lark import Token

from .die import DiceSize, Die
from .node import ASTNode, Number
from .operators import AdvantageCategory, Operator, OperatorCategory, Selector
from ..context import RollContext
from ..distribution import ConvolutionDistributionBuilder, DiscreteDistributionBuilder, Distribution
from ..errors import RollError, RollValueError

TNumber = TypeVar("TNumber", bound=Number)


def find_from_advantage(rolls: Sequence[TNumber], adv: OperatorCategory | None) -> TNumber:
    if adv == "adv":
        return sorted(rolls, key=lambda r: r.total, reverse=True)[0]
    elif adv == "dis":
        return sorted(rolls, key=lambda r: r.total, reverse=False)[0]

    return rolls[0]


class Dice(Number):
    """Represents a set of dice."""

    dice: list[Die]
    count: int
    size: DiceSize
    operators: list["Operator"]
    _context: RollContext

    def __init__(
        self,
        dice: list[Die],
        count: int,
        size: DiceSize,
        operators: list["Operator"],
        ast: ASTNode,
        context: RollContext,
    ) -> None:
        super().__init__(ast)
        self.dice = dice
        self._context = context

        self.count = count
        self.size = size
        self.operators = operators

    @classmethod
    def _new_single(cls, ast: "ASTDice", context: RollContext) -> "Dice":
        num = ast.num
        size = ast.size
        dice: list[Die] = []
        operators = ast.operations

        for _ in range(num):
            die = Die.new(size, context)
            dice.append(die)

        result = cls(dice, num, size, operators, ast, context)
        for operator in operators:
            # Skip adv and dis operators, this should be handled by Dice.new
            if operator.op in ["adv", "dis"]:
                continue
            result.operate(operator)

        return result

    @classmethod
    def new(cls, ast: "ASTDice", context: RollContext) -> tuple["Dice", list["Dice"]]:
        """Roll a new set of dice."""
        adv: AdvantageCategory | None = None
        roll_count = 1

        for operator in ast.operations:
            if operator.op == "adv" or operator.op == "dis":
                if adv is not None:
                    raise ValueError(f"Encountered {operator.op} in expression, but expression already has {adv}.")
                adv = operator.op
                roll_count = operator.sel.num

        if roll_count < 1:
            raise ValueError(f"Operator {adv} expected at least one roll.")

        rolls: list[Dice] = []
        for _ in range(roll_count):
            rolls.append(Dice._new_single(ast, context))

        roll = find_from_advantage(rolls, adv)
        return roll, rolls

    @property
    def keptset(self) -> Sequence[Die]:
        """Return a list of all dice that were not dropped."""
        return [die for die in self.dice if die.kept]

    @property
    def total(self) -> int:
        return sum(die.value for die in self.keptset)

    @property
    def children(self) -> Sequence[Number]:
        return []

    def roll_another(self, negative: bool = False) -> None:
        """Roll another die and add it to the dice set."""
        die = Die.new(self.size, self._context)

        if negative:
            die.set_value(-die.value)

        self.dice.append(die)

    def __repr__(self) -> str:
        operators = "".join(repr(operator) for operator in self.operators)
        return f"<Dice num={self.count} size={self.size} operators={operators} total={self.total}/>"

    def copy(self) -> "Dice":
        dice = [die.copy() for die in self.dice]
        return Dice(dice, self.count, self.size, self.operators, self.ast, self._context)

    def extract_dice(self) -> Sequence[Die]:
        return list(self.keptset)

    # region ==== Selector ====

    def select(self, selector: Selector) -> set[Die]:
        if selector.cat == "h":
            selected = sorted(self.keptset, key=lambda n: n.value, reverse=True)[: selector.num]
            return set(selected)

        if selector.cat == "l":
            selected = sorted(self.keptset, key=lambda n: n.value, reverse=False)[: selector.num]
            return set(selected)

        return set(die for die in self.keptset if selector.matches(die.value))

    # endregion ==== Selector ====

    # region ==== Operator ====

    def operate(self, operator: "Operator") -> None:
        """Apply an operator to the dice set."""
        operations: Mapping[OperatorCategory, Callable[[Selector], None]] = {
            # set only
            "k": self.keep,
            "p": self.drop,
            # dice only
            "rr": self.reroll,
            "ro": self.reroll_once,
            "ra": self.explode_once,
            "e": self.explode,
            "rs": self.reroll_and_subtract,
            "mi": self.minimum,
            "ma": self.maximum,
            # expr only
            "red": self.explode_red,
        }

        operations[operator.op](operator.sel)

    def keep(self, selector: Selector) -> None:
        for value in self.keptset:
            if value not in self.select(selector):
                value.drop()

    def drop(self, selector: Selector) -> None:
        for value in self.select(selector):
            value.drop()

    def reroll(self, selector: Selector) -> None:
        to_reroll = self.select(selector)

        while to_reroll:
            for die in to_reroll:
                die.reroll()

            to_reroll = self.select(selector)

    def reroll_once(self, selector: Selector) -> None:
        for die in self.select(selector):
            die.reroll()

    def explode(self, selector: Selector) -> None:
        to_explode = self.select(selector)
        already_exploded: set[Die] = set()

        while to_explode:
            for die in to_explode:
                if not die.exploded:
                    die.explode()
                    self.roll_another()

            already_exploded.update(to_explode)
            to_explode = (self.select(selector)).difference(already_exploded)

    def explode_once(self, selector: Selector) -> None:
        for die in self.select(selector):
            if not die.exploded:
                die.explode()
                self.roll_another()
                return

    def reroll_and_subtract(self, selector: Selector) -> None:
        for die in self.select(selector):
            if not die.exploded:
                die.explode()
                self.roll_another(negative=True)
                return

    def explode_red(self, selector: Selector) -> None:
        if self.size == "%":
            size = 100
        else:
            size = self.size

        rolled_values = [die.value for die in self.dice]
        rs_count = rolled_values.count(1)
        ra_count = rolled_values.count(size)

        if ra_count > 0:
            self.roll_another(negative=False)
        if rs_count > 0:
            self.roll_another(negative=True)

    def minimum(self, selector: Selector) -> None:
        if selector.cat is not None:
            raise RollValueError(f"{str(selector)} is not a valid selector for minimums.")
        the_min = selector.num
        for die in self.keptset:
            if die.value < the_min:
                die.set_value(the_min)

    def maximum(self, selector: Selector) -> None:
        if selector.cat is not None:
            raise RollValueError(f"{str(selector)} is not a valid selector for maximums.")
        the_max = selector.num
        for die in self.keptset:
            if die.value > the_max:
                die.set_value(the_max)

    # endregion ==== Operator ====


class ASTDice(ASTNode):
    """A dice is a collection of die with or without operators."""

    num: int
    size: DiceSize
    operations: list[Operator]

    def __init__(self, num: int | Token, size: int | str | Token, *operations: Operator):
        super().__init__()
        self.num = int(num)
        if str(size) == "%":
            self.size = "%"
        else:
            self.size = int(size)
        self.operations = list(operations)
        self._validate_operations()

    @property
    def children(self) -> Sequence[ASTNode]:
        return []

    def _sides(self) -> int:
        if self.size == "%":
            return 100
        else:
            return self.size

    def _validate_operations(self):
        """Validates if the operations are valid."""
        # Only one adv or dis allowed per expression
        adv_count = 0
        for op in self.operations:
            if op.op in ["adv", "dis"]:
                adv_count += 1
                # adv or dis selector must a numeric value greater than zero
                if op.sel.cat is not None or op.sel.num < 1:
                    raise RollError(f"Selector for {op} must be a numeric value greater than zero.")

        if adv_count > 1:
            raise RollError("Only one adv or dis operator is allowed per dice expression.")

    def copy(self) -> "ASTDice":
        operations = [op.copy() for op in self.operations]
        return ASTDice(self.num, self.size, *operations)

    def __str__(self):
        operations = "".join([str(op) for op in self.operations])
        return f"{self.num}d{self.size}{operations}"

    def roll(self, context: RollContext) -> tuple[Dice, list[Dice]]:
        return Dice.new(self, context)

    def distribution(self) -> Distribution:
        count = self.num
        sides = self._sides()
        operations = self.operations

        contains_non_convolution_operation = any(
            not ConvolutionDistributionBuilder.supports_operation(op) for op in operations
        )

        if contains_non_convolution_operation:
            builder = DiscreteDistributionBuilder(count, sides, operations)
        else:
            builder = ConvolutionDistributionBuilder(count, sides, operations)

        return builder.distribution()

    @property
    def is_comparison(self) -> bool:
        return False

    def find_dice(self, count: int, size: DiceSize) -> "ASTDice | None":
        if self.num == count and self.size == size:
            return self
        return None
