from typing import Literal

from ..context import RollContext

DiceSize = int | Literal["%"]


class Die:
    """Represents a single die that can be rerolled or dropped."""

    kept: bool
    exploded: bool
    size: DiceSize
    values: list[int]  # history of values, the last one is the most recent one
    _context: RollContext

    def __init__(
        self,
        value: int | list[int],
        size: DiceSize,
        context: RollContext,
        kept: bool = True,
        exploded: bool = False,
    ) -> None:
        self.size = size
        self._context = context
        self.kept = kept
        self.exploded = exploded

        if isinstance(value, int):
            self.values = [value]
        else:
            self.values = value

    @property
    def value(self) -> int:
        """The final value of the die."""
        return self.values[-1]

    def reroll(self) -> None:
        """Re-roll the current die."""
        roll = self._context.roll(self.size)
        self.values.append(roll)

    def set_value(self, value: int) -> None:
        """Set the current value of the die forcibly."""
        self.values.append(value)

    def drop(self) -> None:
        """Mark the die as dropped."""
        self.kept = False

    def explode(self) -> None:
        """Mark the die as exploded."""
        self.exploded = True

    @staticmethod
    def new(size: DiceSize, context: RollContext, kept: bool = True, exploded: bool = False) -> "Die":
        """Roll a new die."""
        value = context.roll(size)
        return Die(value, size, context, kept=kept, exploded=exploded)

    def copy(self) -> "Die":
        """Return a copy of the die."""
        return Die(value=[*self.values], size=self.size, context=self._context, kept=self.kept, exploded=self.exploded)
