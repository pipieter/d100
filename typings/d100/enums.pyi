from enum import Enum

__all__ = ["Critical"]

class Critical(str, Enum):
    """Enumeration representing the crit type of a roll."""

    NONE = "none"
    CRIT = "crit"
    FAIL = "fail"
    DIRTY = "dirty"
