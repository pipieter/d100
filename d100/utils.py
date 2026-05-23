from collections.abc import Sequence

from d100.ast.literal import ASTLiteral, Literal
from .ast.binop import ASTBinOp, BinOp
from .ast.dice import ASTDice, Dice, Die
from .ast.expression import ASTExpression, Expression
from .ast.node import ASTNode, Number
from .ast.operators import AdvantageCategory, Operator, Selector
from .ast.parenthetical import ASTParenthetical, Parenthetical
from .ast.unop import ASTUnOp, UnOp
from .enums import Critical


def find_d20(node: ASTNode) -> ASTDice | None:
    """
    Find the first fitting node that represents a d20 in a standard d20 plus modifiers roll.

    Args:
        node (ast.Node): The root node of the tree to search in.

    Raises:
        NotImplementedError: If an unknown node type is encountered.

    Returns:
        ast.Dice | None: A dice object representing the d20, or None if none could be found.
    """
    if isinstance(node, ASTExpression):
        return find_d20(node.value)

    if isinstance(node, ASTParenthetical):
        return find_d20(node.value)

    if isinstance(node, ASTLiteral):
        return None

    if isinstance(node, ASTUnOp):
        return find_d20(node.value)

    if isinstance(node, ASTBinOp):
        if node.op not in ["+", "-"]:
            return None

        left = find_d20(node.left)
        if left is not None:
            return left

        right = find_d20(node.right)
        if right is not None:
            return right

        return None

    if isinstance(node, ASTDice):
        if node.num == 1 and node.size == 20:
            return node
        return None

    raise NotImplementedError(f"find_d20 not implemented for {type(node)}")


def determine_crit_type(root: Number, d20: Number | None) -> Critical:
    if isinstance(d20, Dice):
        dice = d20.keptset
    else:
        return Critical.NONE

    if len(dice) != 1 or d20.size != 20:
        return Critical.NONE

    if dice[0].value == 1:
        return Critical.FAIL

    if dice[0].value == 20:
        return Critical.CRIT

    if root.total == 20 and dice[0].value != 20:
        return Critical.DIRTY

    return Critical.NONE


def add_adv_operator_to_dice(dice: ASTDice, adv: AdvantageCategory | None, count: int) -> bool:
    if adv is None:
        return True

    # Check if the dice already has adv or dis
    for operator in dice.operations:
        if operator.op in ["adv", "dis"]:
            return False

    dice.operations.append(Operator(adv, [Selector(None, count)]))
    return True


def extract_dice(node: Number) -> Sequence[Die]:
    if isinstance(node, Expression):
        return extract_dice(node.value)
    if isinstance(node, Literal):
        return []
    if isinstance(node, Dice):
        return node.keptset
    if isinstance(node, Parenthetical):
        return extract_dice(node.value)
    if isinstance(node, UnOp):
        return extract_dice(node.value)
    if isinstance(node, BinOp):
        return list(extract_dice(node.left)) + list(extract_dice(node.right))

    raise NotImplementedError(f"extract_dice not implemented for {type(node)}")


def expression_is_comparison(node: ASTNode) -> bool:
    if isinstance(node, ASTExpression):
        return expression_is_comparison(node.value)
    if isinstance(node, ASTParenthetical):
        return expression_is_comparison(node.value)
    if isinstance(node, ASTBinOp):
        return node.op in {">", "<", ">=", "<=", "==", "!="}

    return False
