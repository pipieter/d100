from enum import Enum
from typing import Literal

__all__ = ["Critical", "Advantage"]

class Critical(str, Enum):
    """Enumeration representing the crit type of a roll."""

    NONE = "none"
    CRIT = "crit"
    FAIL = "fail"
    DIRTY = "dirty"

class Advantage(str, Enum):
    """Enumeration representing at what advantage a roll should be made at."""

    NONE = "none"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"
    ELVEN_ACCURACY = "elven accuracy"
    @property
    def rolls(self) -> int: ...
    @property
    def adv(self) -> Literal["adv", "dis", None]: ...
