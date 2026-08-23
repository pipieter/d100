import os
import string
import typing
from collections.abc import MutableMapping
from typing import Any, TypeGuard

import cachetools
import lark
from lark import Lark, Token, Transformer

from .ast.binop import ASTBinOp
from .ast.dice import ASTDice
from .ast.expression import ASTExpression
from .ast.literal import ASTLiteral
from .ast.node import ASTNode
from .ast.operators import (
    AdvantageCategory,
    BinaryOperator,
    DiceCategory,
    ExpressionCategory,
    Operator,
    Selector,
    SelectorNew,
    SetCategory,
    UnaryOperator,
    ValueSelector,
)
from .ast.parenthetical import ASTParenthetical
from .ast.unop import ASTUnOp
from .errors import RollError, RollSyntaxError


class RollTransformer(Transformer[Any, Any]):
    def _is_unop(self, op: Token | str) -> TypeGuard[UnaryOperator]:
        op = str(op)
        return op in typing.get_args(UnaryOperator)

    def _is_binop(self, op: Token | str) -> TypeGuard[BinaryOperator]:
        op = str(op)
        return op in typing.get_args(BinaryOperator)

    def expr(self, expr: tuple[ASTNode]) -> ASTExpression:
        (value,) = expr
        return ASTExpression(value)

    def comparison(self, binop: tuple[ASTNode, Token, ASTNode]) -> ASTBinOp:
        left, op, right = binop

        if not self._is_binop(op):
            raise RollError(f"Invalid binary operator: '{op}'")

        return ASTBinOp(left, op, right)

    def a_num(self, binop: tuple[ASTNode, Token, ASTNode]) -> ASTBinOp:
        left, op, right = binop

        if not self._is_binop(op):
            raise RollError(f"Invalid binary operator: '{op}'")

        return ASTBinOp(left, op, right)

    def m_num(self, binop: tuple[ASTNode, Token, ASTNode]) -> ASTBinOp:
        left, op, right = binop

        if not self._is_binop(op):
            raise RollError(f"Invalid binary operator: '{op}'")

        return ASTBinOp(left, op, right)

    def u_num(self, unop: tuple[Token, ASTNode]) -> ASTUnOp:
        op, value = unop

        if not self._is_unop(op):
            raise RollError(f"Invalid unary operator: '{op}'")

        return ASTUnOp(op, value)

    def literal(self, literal: tuple[Token]) -> ASTLiteral:
        (value,) = literal
        if value.type == "INTEGER":
            return ASTLiteral(int(value))
        if value.type == "DECIMAL":
            return ASTLiteral(float(value))

        raise SyntaxError(f"Unsupported literal type {value.type}")

    def parenthetical(self, num: tuple[ASTNode] | tuple[ASTNode, Operator]) -> ASTParenthetical:
        if len(num) == 1:
            (value,) = num
            return ASTParenthetical(value, None)
        else:
            value, operator = num
            return ASTParenthetical(value, operator)

    def dice(self, opdice: Any) -> ASTDice:
        dice, *operations = opdice
        return ASTDice(dice.num, dice.size, *operations)

    def dice_op(self, opsel: tuple[Operator]) -> Operator:
        return opsel[0]

    def dice_expr(self, dice: Any) -> ASTDice:
        if len(dice) == 1:
            return ASTDice(1, *dice)
        return ASTDice(*dice)

    def selector(self, sel: Any) -> Selector:
        return SelectorNew(*sel)

    def num_selector(self, sel: Any) -> Selector:
        return ValueSelector(None, *sel)

    def dice_operator(self, opsel: tuple[DiceCategory, Selector]) -> Operator:
        op, sel = opsel
        return Operator.new(op, sel)

    def set_operator(self, opsel: tuple[SetCategory, Selector]) -> Operator:
        op, sel = opsel
        return Operator.new(op, sel)

    def advantage_operator(self, opsel: tuple[AdvantageCategory] | tuple[AdvantageCategory, int]) -> Operator:
        if len(opsel) == 1:
            (op,) = opsel
            return Operator.new(op, ValueSelector(None, 2))

        op, sel = opsel
        return Operator.new(op, ValueSelector(None, sel))

    def expression_operator(self, opsel: tuple[ExpressionCategory]) -> Operator:
        (op,) = opsel
        return Operator.new(op)


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

    @staticmethod
    def _remove_whitespace(chars: str) -> str:
        chars = chars.strip()
        for ws in string.whitespace:
            chars = chars.strip(ws)
            chars = chars.replace(ws, "")
        return chars

    def parse(self, expr: str | bytes, start: str | None = None) -> ASTExpression:
        """Parse an expression string to an expression AST tree."""
        if start is None:
            start = "expr"

        clean_expr = self._remove_whitespace(str(expr))
        try:
            # see if this expr is in cache
            if clean_expr in self._cache:
                dice_tree = self._cache[clean_expr].copy()  # create a copy in case the user changes the tree
            else:
                dice_tree = self._lark.parse(clean_expr, start=start)  # type: ignore
                dice_tree = typing.cast(ASTExpression, dice_tree)
                self._cache[clean_expr] = dice_tree
            return dice_tree
        except lark.UnexpectedToken as ut:
            raise RollSyntaxError(clean_expr, ut.line, ut.column, ut.token, ut.expected)
        except lark.UnexpectedCharacters as uc:
            raise RollSyntaxError(clean_expr, uc.line, uc.column, clean_expr[uc.pos_in_stream], uc.allowed)


if __name__ == "__main__":
    grammar_path = os.path.join(os.path.dirname(__file__), "grammar.lark")
    parser = Parser(grammar_path)

    while True:
        expr = parser.parse(input("> "), start="expr")
        print(str(expr))
