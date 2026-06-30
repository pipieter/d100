import abc
from collections.abc import Sequence
from typing import Self

from .dice import ASTDice as ASTDice
from .die import DiceSize as DiceSize, Die as Die
from ..context import RollContext as RollContext
from ..distribution import Distribution as Distribution

class Number(abc.ABC, metaclass=abc.ABCMeta):
    """The base class for all rolled values."""

    ast: ASTNode
    def __init__(self, ast: ASTNode) -> None: ...
    @property
    @abc.abstractmethod
    def total(self) -> int:
        """The total value of the Number."""
    @property
    @abc.abstractmethod
    def children(self) -> Sequence["Number"]:
        """The children of the node."""
    @abc.abstractmethod
    def copy(self) -> Number:
        """Return a copy of the Number. The original AST nodes will not be copied to still allow find_from_ast."""
    def find_from_ast(self, ast: ASTNode | None) -> Number | None:
        """Find the child of the evaluated Number from its original AST node, or None if it could not be found."""
    @abc.abstractmethod
    def extract_dice(self) -> Sequence[Die]:
        """Extract all rolled dice in the entire number, including children."""

class ASTNode(abc.ABC, metaclass=abc.ABCMeta):
    """The base class for all AST nodes."""

    @abc.abstractmethod
    def copy(self) -> Self:
        """Create a copy of the node."""
    @property
    @abc.abstractmethod
    def children(self) -> Sequence["ASTNode"]:
        """Retrieve all children of the node."""
    @abc.abstractmethod
    def roll(self, context: RollContext) -> tuple["Number", Sequence["Number"]]:
        """Roll a node and get its result."""
    @abc.abstractmethod
    def distribution(self) -> Distribution:
        """Build a distribution of the node."""
    @property
    @abc.abstractmethod
    def is_comparison(self) -> bool:
        """Return whether or not the node is a binary comparison."""
    @abc.abstractmethod
    def find_dice(self, count: int, size: DiceSize) -> ASTDice | None:
        """Find the first standalone dice object with a number of sides and a specific size."""
    def find_d20(self) -> ASTDice | None: ...
