import os
import typing
from collections.abc import MutableMapping
from typing import Any, Optional, TypeGuard

import cachetools
import lark
from lark import Lark, Token, Transformer

from .ast.unevaluated import ASTUnevaluated

from .ast.binop import ASTBinOp
from .ast.dice import ASTDice
from .ast.expression import ASTExpression
from .ast.literal import ASTLiteral
from .ast.node import ASTNode
from .ast.operators import BinaryOperator, Operator, OperatorCategory, Selector, UnaryOperator
from .ast.parenthetical import ASTParenthetical
from .ast.unop import ASTUnOp
from .errors import RollError, RollSyntaxError


class DiceTransformer(Transformer[Any, Any]):
    def expr(self, expr: tuple[Any, ...]) -> ASTLiteral | ASTDice:
        (value,) = expr
        if hasattr(value, "type") and value.type == "INT":
            return ASTLiteral(int(str(value)))

        if hasattr(value, "type") and value.type == "DECIMAL":
            return ASTLiteral(float(str(value)))

        return value

    def dice(self, opdice: Any) -> ASTDice:
        dice, *operations = opdice
        return ASTDice(dice.num, dice.size, *operations)

    def dice_operator(self, opsel: tuple[OperatorCategory, Optional[Selector]]) -> Operator:
        return Operator.new(*opsel)

    def dice_expr(self, dice: Any) -> ASTDice:
        if len(dice) == 1:
            return ASTDice(1, *dice)
        return ASTDice(*dice)

    def selector(self, sel: Any) -> Selector:
        return Selector(*sel)

    def num_selector(self, sel: Any) -> Selector:
        return Selector(None, *sel)


class ExpressionTransformer(Transformer[Any, Any]):
    _dice_grammar: Lark

    def __init__(self, dice_grammar: Lark) -> None:
        super().__init__(visit_tokens=True)
        self._dice_grammar = dice_grammar

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

    def parenthetical(self, num: Any) -> ASTParenthetical:
        return ASTParenthetical(*num)

    def value(self, token: tuple[Token]) -> ASTLiteral | ASTDice | ASTUnevaluated:
        (value,) = token
        if value.type == "INT":
            return ASTLiteral(int(value))

        if value.type == "DECIMAL":
            return ASTLiteral(float(value))

        # If it's not an int or a float, it's string and a potential dice expression
        value = str(value)

        try:
            return self._dice_grammar.parse(value, start="expr")  # type: ignore
        except:
            # If the expression could not have been parsed as a dice, it must non-evaluatable
            return ASTUnevaluated(value)

    def unevaluated(self, unevaluated: str) -> ASTUnevaluated:
        return ASTUnevaluated(unevaluated)


class Parser:
    _lark: Lark
    _cache: MutableMapping[str, ASTExpression]
    _dice_transformer: DiceTransformer
    _expression_transformer: ExpressionTransformer

    def __init__(self, dice_grammar_path: str, expression_grammar_path: str) -> None:
        with open(dice_grammar_path, "r") as dice_grammar_file:
            dice_grammar = dice_grammar_file.read()

        with open(expression_grammar_path, "r") as expression_grammar_file:
            expression_grammar = expression_grammar_file.read()

        self._dice_transformer = DiceTransformer()
        self._dice_lark = Lark(
            dice_grammar,
            start=["expr"],
            parser="lalr",
            transformer=self._dice_transformer,
            maybe_placeholders=True,
        )

        self._expression_transformer = ExpressionTransformer(self._dice_lark)
        self._cache = cachetools.LFUCache(256)
        self._lark = Lark(
            expression_grammar,
            start=["expr"],
            parser="lalr",
            transformer=self._expression_transformer,
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
                dice_tree = self._cache[clean_expr].copy()  # create a copy in case the user changes the tree
            else:
                dice_tree = self._lark.parse(expr, start=start)  # type: ignore
                dice_tree = typing.cast(ASTExpression, dice_tree)
                self._cache[clean_expr] = dice_tree
            return dice_tree
        except lark.UnexpectedToken as ut:
            raise RollSyntaxError.from_unexpected(ut.line, ut.column, ut.token, ut.expected)
        except lark.UnexpectedCharacters as uc:
            raise RollSyntaxError.from_unexpected(uc.line, uc.column, expr[uc.pos_in_stream], uc.allowed)


if __name__ == "__main__":
    dice_grammar_path = os.path.join(os.path.dirname(__file__), "lark", "dice.lark")
    expression_grammar_path = os.path.join(os.path.dirname(__file__), "lark", "expression.lark")
    parser = Parser(dice_grammar_path=dice_grammar_path, expression_grammar_path=expression_grammar_path)

    while True:
        expr = parser.parse(input("> "), start="expr")
        print(str(expr))
