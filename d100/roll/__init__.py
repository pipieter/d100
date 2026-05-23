# region ===== Roller ======

import dataclasses
import random
from typing import Optional

from .stringifier import SimpleStringifier, Stringifier
from .. import utils
from ..ast.node import ASTNode, Number
from ..context import RollContext
from ..enums import Advantage, Critical
from ..rand import random_impl


@dataclasses.dataclass
class SingleRollResult:
    """Holds information of a single roll result."""

    ast: ASTNode
    roll: Number
    crit: Critical
    stringifier: Stringifier

    @property
    def expr(self) -> str:
        """Return the string representation of the evaluated expression."""
        return self.stringifier.stringify(self.roll)

    @property
    def total(self) -> int:
        """Return the total value of the roll."""
        return self.roll.total

    @property
    def is_comparison(self) -> bool:
        """Checks if the roll is a top-level comparison."""
        return utils.expression_is_comparison(self.ast)


@dataclasses.dataclass
class RollResult:
    """Holds information about the result of a roll. This should generally not be constructed manually."""

    ast: ASTNode
    roll: SingleRollResult
    rolls: list[SingleRollResult]
    advantage: Advantage
    stringifier: Stringifier
    warnings: list[str]

    @property
    def total(self) -> int:
        """Return the total value of the roll."""
        return self.roll.total

    @property
    def result(self) -> str:
        """Return the stringified expression of the result, e.g. 1d20 (5) + 2 = 7"""
        return self.roll.expr

    @property
    def expression(self) -> str:
        """Return the original form of the expression, e.g. 1d20 + 2"""
        return str(self.ast)

    def __int__(self) -> int:
        """Return the total value of the expression, as an integer."""
        return int(self.total)

    def __float__(self) -> float:
        """Return the total value of the expression, as an floating point number.."""
        return float(self.total)

    def __repr__(self) -> str:
        return f"<RollResult total={self.total}/>"


class Roller:
    """The main class responsible for evaluating and rolling dice expressions."""

    _rng: random.Random

    def __init__(self, rng: random.Random = random_impl):
        self._rng = rng

    def seed(self, s: int | float | str | bytes | bytearray | None = None) -> None:
        """Set the seed of the rng."""
        self._rng.seed(s)

    def roll(
        self,
        node: ASTNode,
        stringifier: Optional[Stringifier] = None,
        advantage: Advantage = Advantage.NONE,
    ) -> RollResult:
        """Rolls the dice."""

        # It's possible for the node to be edited for advantage, so a copy is made
        node = node.copy()

        if stringifier is None:
            stringifier = SimpleStringifier()

        d20 = utils.find_d20(node)
        context = RollContext(self._rng)
        warnings: list[str] = []

        # Add the advantage operator
        if advantage != Advantage.NONE:
            if d20 is None:
                warnings.append(f"Rolled with {advantage.value}, but expression did not contain a valid d20.")
            else:
                if not utils.add_adv_operator_to_dice(d20, advantage.adv, advantage.rolls):
                    warnings.append(f"The d20 in the expression already had an advantage operator.")

        # Roll the actual die
        roll, rolls = node.roll(context)

        # Add die warning
        die = utils.extract_dice(roll)
        if len(die) == 0:
            warnings.append("Expression did not contain any dice.")

        results = [
            SingleRollResult(
                ast=node,
                roll=roll,
                stringifier=stringifier,
                crit=utils.determine_crit_type(roll, roll.find_from_ast(d20)),
            )
            for roll in rolls
        ]
        result = results[rolls.index(roll)]

        return RollResult(
            ast=node,
            roll=result,
            rolls=results,
            advantage=advantage,
            stringifier=stringifier,
            warnings=warnings,
        )
