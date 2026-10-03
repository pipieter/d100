from ..ast.binop import ASTBinOp
from ..ast.dice import ASTDice
from ..ast.die import DiceSize
from ..ast.node import ASTNode


def find_dice(expr: ASTNode, num: int, size: DiceSize) -> ASTDice | None:
    if isinstance(expr, ASTDice):
        if expr.num == num and expr.size == size:
            return expr

    if isinstance(expr, ASTBinOp):
        allowed_binops = ["+", "-"]
        if expr.op not in allowed_binops:
            return None

        left = find_dice(expr.left, num, size)
        if left:
            return left

        right = find_dice(expr.right, num, size)
        if right:
            return right

        return None

    for child in expr.children:
        found = find_dice(child, num, size)
        if found:
            return found

    return None


def find_d20(expr: ASTNode) -> ASTDice | None:
    return find_dice(expr, 1, 20)
