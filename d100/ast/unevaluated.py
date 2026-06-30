from collections.abc import Sequence
from typing import Literal

from .dice import ASTDice
from .node import ASTNode, Number
from ..context import RollContext
from ..distribution import Distribution
from ..errors import RollSyntaxError


class ASTUnevaluated(ASTNode):
    value: str

    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = value

    def copy(self) -> "ASTUnevaluated":
        return ASTUnevaluated(self.value)

    def __str__(self) -> str:
        return str(self.value)

    @property
    def children(self) -> Sequence[ASTNode]:
        return []

    def roll(self, context: RollContext) -> tuple[Number, Sequence[Number]]:
        raise RollSyntaxError(f"Cannot roll an unevaluated value '{self.value}'")

    def distribution(self) -> Distribution:
        raise RollSyntaxError(f"Cannot create the distribution of an unevaluated value '{self.value}'")

    @property
    def is_comparison(self) -> bool:
        return False

    def find_dice(self, count: int, size: int | Literal["%"]) -> ASTDice | None:
        return None
