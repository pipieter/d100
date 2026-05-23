import random
from typing import Literal

from _typeshed import Incomplete

from .errors import RollValueError as RollValueError, TooManyRolls as TooManyRolls

class RollContext:
    """
    A class to track information about rolls to ensure all rolls halt eventually.

    To use this class, pass an instance to the constructor of `Roller`.
    """

    rng: Incomplete
    max_rolls: Incomplete
    rolls: int
    def __init__(self, rng: random.Random, max_rolls: int = 1000) -> None: ...
    def roll(self, size: int | Literal["%"]) -> int:
        """Roll a dice and return its value."""
