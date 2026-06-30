from typing import Any

__all__ = ["RollError", "RollSyntaxError", "RollValueError", "TooManyRolls"]

class RollError(Exception):
    """Generic exception happened in the roll. Base exception for all library exceptions."""

    def __init__(self, msg: str) -> None: ...

class RollSyntaxError(RollError):
    """Syntax error happened while parsing roll."""

    @staticmethod
    def from_unexpected(line: int, col: int, got: Any, expected: Any) -> RollSyntaxError: ...

class RollValueError(RollError):
    """A bad value was passed to an operator."""

class TooManyRolls(RollError):
    """Too many dice rolled (in an individual dice or in rerolls)."""
