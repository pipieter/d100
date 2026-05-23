import os

from .ast.expression import ASTExpression
from .distribution import Distribution
from .enums import *
from .errors import *
from .parser import Parser
from .rand import random_impl
from .roll import Roller, RollResult
from .roll.stringifier import Stringifier

_grammar_path = os.path.join(os.path.dirname(__file__), "grammar.lark")
_parser = Parser(_grammar_path)
_roller = Roller(random_impl)


def parse(expr: str | ASTExpression) -> ASTExpression:
    if isinstance(expr, str):
        return _parser.parse(expr)
    return expr


def roll(
    expr: str | ASTExpression, stringifier: Stringifier | None = None, advantage: Advantage = Advantage.NONE
) -> RollResult:
    tree = parse(expr)
    return _roller.roll(tree, stringifier, advantage)


def seed(s: int | float | str | bytes | bytearray | None = None) -> None:
    _roller.seed(s)


def distribution(expr: str | ASTExpression) -> Distribution:
    tree = parse(expr)
    roll(tree)  # Roll the expression once to see if it works
    return tree.distribution()
