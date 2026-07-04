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

                if len(operator.sels) == 0:
                    roll_count = 2
                elif len(operator.sels) != 1:
                    raise ValueError(f"Operator {operator.op} expected one selector.")
                else:
                    if operator.sels[0].cat is not None:
                        raise ValueError(f"Operator {operator.op} only works with literal numerics.")

                    roll_count = operator.sels[0].num

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

    def select(self, selectors: list[Selector]) -> set[Die]:
        out: set[Die] = set()
        for sel in selectors:
            out.update(self.select_single(sel))
        return out

    def select_single(self, selector: Selector) -> set[Die]:
        select_functions = {
            "l": self.select_lowest,
            "h": self.select_highest,
            "<": self.select_less_than,
            ">": self.select_more_than,
            None: self.select_literal,
        }
        return set(select_functions[selector.cat](selector.num))

    def select_lowest(self, value: int) -> Sequence[Die]:
        return sorted(self.keptset, key=lambda n: n.value)[:value]

    def select_highest(self, value: int) -> Sequence[Die]:
        return sorted(self.keptset, key=lambda n: n.value, reverse=True)[:value]

    def select_less_than(self, value: int) -> Sequence[Die]:
        return [n for n in self.keptset if n.value < value]

    def select_more_than(self, value: int) -> Sequence[Die]:
        return [n for n in self.keptset if n.value > value]

    def select_literal(self, value: int) -> Sequence[Die]:
        return [n for n in self.keptset if n.value == value]

    # endregion ==== Selectro ====

    # region ==== Operator ====

    def operate(self, operator: "Operator") -> None:
        """Apply an operator to the dice set."""
        operations: Mapping[OperatorCategory, Callable[[list[Selector]], None]] = {
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

        operations[operator.op](operator.sels)

    def keep(self, selectors: list[Selector]) -> None:
        for value in self.keptset:
            if value not in self.select(selectors):
                value.drop()

    def drop(self, selectors: list[Selector]) -> None:
        for value in self.select(selectors):
            value.drop()

    def reroll(self, selectors: list[Selector]) -> None:
        to_reroll = self.select(selectors)

        while to_reroll:
            for die in to_reroll:
                die.reroll()

            to_reroll = self.select(selectors)

    def reroll_once(self, selectors: list[Selector]) -> None:
        for die in self.select(selectors):
            die.reroll()

    def explode(self, selectors: list[Selector]) -> None:
        to_explode = self.select(selectors)
        already_exploded: set[Die] = set()

        while to_explode:
            for die in to_explode:
                if not die.exploded:
                    die.explode()
                    self.roll_another()

            already_exploded.update(to_explode)
            to_explode = (self.select(selectors)).difference(already_exploded)

    def explode_once(self, selectors: list[Selector]) -> None:
        for die in self.select(selectors):
            if not die.exploded:
                die.explode()
                self.roll_another()
                return

    def reroll_and_subtract(self, selectors: list[Selector]) -> None:
        for die in self.select(selectors):
            if not die.exploded:
                die.explode()
                self.roll_another(negative=True)
                return

    def explode_red(self, selectors: list[Selector]) -> None:
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

    def minimum(self, selectors: list[Selector]) -> None:
        selector = selectors[-1]
        if selector.cat is not None:
            raise RollValueError(f"{str(selector)} is not a valid selector for minimums.")
        the_min = selector.num
        for die in self.keptset:
            if die.value < the_min:
                die.set_value(the_min)

    def maximum(self, selectors: list[Selector]) -> None:
        """
        :type target: Dice
        """
        selector = selectors[-1]
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
                for sel in op.sels:
                    if sel.cat is not None or sel.num < 1:
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
