import os
import typing
from collections.abc import MutableMapping
from typing import Any, Optional

import cachetools
import lark
from lark import Lark, Token, Transformer

from .ast.binop import ASTBinOp
from .ast.dice import ASTDice
from .ast.expression import ASTExpression
from .ast.literal import ASTLiteral
from .ast.node import ASTNode
from .ast.operators import Operator, OperatorCategory, Selector
from .ast.parenthetical import ASTParenthetical
from .ast.unop import ASTUnOp
from .errors import RollSyntaxError

# ===== transformer, parser -> ast =====

DiceSize = int | typing.Literal["%"]


# noinspection PyMethodMayBeStatic
class RollTransformer(Transformer[Any, Any]):
    def expr(self, expr: tuple[ASTNode]) -> ASTExpression:
        (value,) = expr
        return ASTExpression(value)

    def comparison(self, binop: tuple[ASTNode, Token, ASTNode]) -> ASTBinOp:
        left, op, right = binop
        return ASTBinOp(left, str(op), right)  # type: ignore

    def a_num(self, binop: tuple[ASTNode, Token, ASTNode]) -> ASTBinOp:
        left, op, right = binop
        return ASTBinOp(left, str(op), right)  # type: ignore

    def m_num(self, binop: tuple[ASTNode, Token, ASTNode]) -> ASTBinOp:
        left, op, right = binop
        return ASTBinOp(left, str(op), right)  # type: ignore

    def u_num(self, unop: tuple[Token, ASTNode]) -> ASTUnOp:
        op, value = unop
        return ASTUnOp(str(op), value)  # type: ignore

    def literal(self, literal: tuple[Token]) -> ASTLiteral:
        (value,) = literal
        if value.type == "INTEGER":
            return ASTLiteral(int(value))
        if value.type == "DECIMAL":
            return ASTLiteral(float(value))

        raise SyntaxError(f"Unsupported literal type {value.type}")

    def parenthetical(self, num: Any) -> ASTParenthetical:
        return ASTParenthetical(*num)

    def dice(self, opdice: Any) -> ASTDice:
        dice, *operations = opdice
        return ASTDice(dice.num, dice.size, *operations)

    def dice_op(self, opsel: tuple[OperatorCategory, Optional[Selector]]) -> Operator:
        return Operator.new(*opsel)

    def dice_expr(self, dice: Any) -> ASTDice:
        if len(dice) == 1:
            return ASTDice(1, *dice)
        return ASTDice(*dice)

    def selector(self, sel: Any) -> Selector:
        return Selector(*sel)

    def num_selector(self, sel: Any) -> Selector:
        return Selector(None, *sel)


class Parser:
    _lark: Lark
    _cache: MutableMapping[str, ASTExpression]
    _transformer: RollTransformer

    def __init__(self, grammar_path: str) -> None:
        with open(grammar_path, "r") as grammar_file:
            grammar = grammar_file.read()

        self._transformer = RollTransformer()
        self._cache = cachetools.LFUCache(256)
        self._lark = Lark(
            grammar,
            start=["expr"],
            parser="lalr",
            transformer=self._transformer,
            maybe_placeholders=True,
        )

    def parse(self, expr: str | bytes, start: str | None = None) -> ASTExpression:
        """Parse an expression string to an expression AST tree."""
        if start is None:
            start = "expr"

        try:
            expr = str(expr)
            # see if this expr is in cache
            clean_expr = expr.replace(" ", "")
            if clean_expr in self._cache:
                dice_tree = self._cache[clean_expr]
            else:
                dice_tree = self._lark.parse(expr, start=start)  # type: ignore
                dice_tree = typing.cast(ASTExpression, dice_tree)
                self._cache[clean_expr] = dice_tree
            return dice_tree
        except lark.UnexpectedToken as ut:
            raise RollSyntaxError(ut.line, ut.column, ut.token, ut.expected)
        except lark.UnexpectedCharacters as uc:
            raise RollSyntaxError(uc.line, uc.column, expr[uc.pos_in_stream], uc.allowed)


if __name__ == "__main__":
    grammar_path = os.path.join(os.path.dirname(__file__), "grammar.lark")
    parser = Parser(grammar_path)

    while True:
        expr = parser.parse(input("> "), start="expr")
        print(str(expr))
