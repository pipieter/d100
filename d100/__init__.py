import os

from .ast.expression import ASTExpression
from .ast.unevaluated import ASTUnevaluated
from .distribution import Distribution
from .enums import *
from .errors import *
from .parser import Parser
from .rand import random_impl
from .roll import Roller, RollResult
from .stringifier import Stringifier

_dice_grammar_path = os.path.join(os.path.dirname(__file__), "lark", "dice.lark")
_expression_grammar_path = os.path.join(os.path.dirname(__file__), "lark", "expression.lark")

_parser = Parser(dice_grammar_path=_dice_grammar_path, expression_grammar_path=_expression_grammar_path)
_roller = Roller(random_impl)


def parse(expr: str | ASTExpression, allow_unevaluated: bool = False) -> ASTExpression:
    if isinstance(expr, str):
        expr = _parser.parse(expr)

    if not allow_unevaluated:
        unevaluated = [node for node in expr.flatten() if isinstance(node, ASTUnevaluated)]
        if unevaluated:
            raise RollSyntaxError(f"Unevaluated node '{str(unevaluated[0])}' found in expression '{str(expr)}'")

    return expr


def roll(expr: str | ASTExpression, stringifier: Stringifier | None = None) -> RollResult:
    tree = parse(expr)
    return _roller.roll(tree, stringifier)


def seed(s: int | float | str | bytes | bytearray | None = None) -> None:
    _roller.seed(s)


def distribution(expr: str | ASTExpression) -> Distribution:
    tree = parse(expr)
    roll(tree)  # Roll the expression once to see if it works
    return tree.distribution()
