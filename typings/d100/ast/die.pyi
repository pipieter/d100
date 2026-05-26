from _typeshed import Incomplete

from ..context import RollContext as RollContext

DiceSize: Incomplete

class Die:
    """Represents a single die that can be rerolled or dropped."""

    kept: bool
    exploded: bool
    size: DiceSize
    values: list[int]
    def __init__(
        self, value: int | list[int], size: DiceSize, context: RollContext, kept: bool = True, exploded: bool = False
    ) -> None: ...
    @property
    def value(self) -> int:
        """The final value of the die."""
    def reroll(self) -> None:
        """Re-roll the current die."""
    def set_value(self, value: int) -> None:
        """Set the current value of the die forcibly."""
    def drop(self) -> None:
        """Mark the die as dropped."""
    def explode(self) -> None:
        """Mark the die as exploded."""
    @staticmethod
    def new(size: DiceSize, context: RollContext, kept: bool = True, exploded: bool = False) -> Die:
        """Roll a new die."""
    def copy(self) -> Die:
        """Return a copy of the die."""
