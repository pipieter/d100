import random
from typing import Literal

from .errors import RollValueError, TooManyRolls


class RollContext:
    """
    A class to track information about rolls to ensure all rolls halt eventually.

    To use this class, pass an instance to the constructor of `Roller`.
    """

    def __init__(self, rng: random.Random, max_rolls: int = 1000):
        self.rng = rng
        self.max_rolls = max_rolls
        self.rolls = 0

    def _increment(self, n: int = 1) -> None:
        """Called each time a die is about to be rolled to avoid too many rolls."""
        self.rolls += n
        if self.rolls > self.max_rolls:
            raise TooManyRolls("Too many dice rolled.")

    def roll(self, size: int | Literal["%"]) -> int:
        """Roll a dice and return its value."""

        if size == 0:
            raise RollValueError("Cannot roll zero-sided die.")

        self._increment(1)
        if size == "%":
            return self.rng.randrange(10) * 10
        else:
            return self.rng.randrange(size) + 1
