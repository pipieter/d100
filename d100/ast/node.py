import abc
from collections.abc import Sequence
from typing import Self

from .die import Die

from ..context import RollContext
from ..distribution import Distribution


class Number(abc.ABC):
    """The base class for all rolled values."""

    ast: "ASTNode"

    def __init__(self, ast: "ASTNode") -> None:
        self.ast = ast

    @property
    @abc.abstractmethod
    def total(self) -> int:
        """The total value of the Number."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def children(self) -> Sequence["Number"]:
        """The children of the node."""
        raise NotImplementedError

    @abc.abstractmethod
    def __repr__(self) -> str:
        """A Python representation of the Number."""
        raise NotImplementedError

    @abc.abstractmethod
    def copy(self) -> "Number":
        """Return a copy of the Number. The original AST nodes will not be copied to still allow find_from_ast."""
        raise NotImplementedError

    def find_from_ast(self, ast: "ASTNode | None") -> "Number | None":
        """Find the child of the evaluated Number from its original AST node, or None if it could not be found."""

        if ast is None:
            return None

        if self.ast == ast:
            return self

        for child in self.children:
            found = child.find_from_ast(ast)
            if found is not None:
                return found

        return None

    @abc.abstractmethod
    def extract_dice(self) -> Sequence[Die]:
        """Extract all rolled dice in the entire number, including children."""
        raise NotImplementedError


class ASTNode(abc.ABC):
    """The base class for all AST nodes."""

    @abc.abstractmethod
    def copy(self) -> Self:
        """Create a copy of the node."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def children(self) -> Sequence["ASTNode"]:
        """Retrieve all children of the node."""
        raise NotImplementedError

    @abc.abstractmethod
    def __str__(self) -> str:
        """Create a string representation of the node."""
        raise NotImplementedError

    @abc.abstractmethod
    def roll(self, context: RollContext) -> tuple["Number", Sequence["Number"]]:
        """Roll a node and get its result."""
        raise NotImplementedError

    @abc.abstractmethod
    def distribution(self) -> Distribution:
        """Build a distribution of the node."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_comparison(self) -> bool:
        """Return whether or not the node is a binary comparison."""
        raise NotImplementedError