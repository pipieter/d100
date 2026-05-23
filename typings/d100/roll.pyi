import dataclasses
import random

from . import utils as utils
from .ast.node import ASTNode as ASTNode, Number as Number
from .context import RollContext as RollContext
from .enums import Advantage as Advantage, Critical as Critical
from .rand import random_impl as random_impl
from .stringifier import SimpleStringifier as SimpleStringifier, Stringifier as Stringifier

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
    @property
    def total(self) -> int:
        """Return the total value of the roll."""
    @property
    def is_comparison(self) -> bool:
        """Checks if the roll is a top-level comparison."""

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
    @property
    def result(self) -> str:
        """Return the stringified expression of the result, e.g. 1d20 (5) + 2 = 7"""
    @property
    def expression(self) -> str:
        """Return the original form of the expression, e.g. 1d20 + 2"""
    def __int__(self) -> int:
        """Return the total value of the expression, as an integer."""
    def __float__(self) -> float:
        """Return the total value of the expression, as an floating point number.."""

class Roller:
    """The main class responsible for evaluating and rolling dice expressions."""

    def __init__(self, rng: random.Random = ...) -> None: ...
    def seed(self, s: int | float | str | bytes | bytearray | None = None) -> None:
        """Set the seed of the rng."""
    def roll(self, node: ASTNode, stringifier: Stringifier | None = None, advantage: Advantage = ...) -> RollResult:
        """Rolls the dice."""
