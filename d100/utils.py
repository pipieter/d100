from .ast.dice import ASTDice, Dice
from .ast.expression import ASTExpression
from .ast.node import Number
from .ast.operators import AdvantageCategory, Operator, OperatorCategory, Selector
from .distribution import Distribution
from .enums import Critical
from .errors import RollError


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


def _add_adv_operator(d20: ASTDice, adv: AdvantageCategory, count: int) -> bool:
    # Check if the dice already has adv or dis
    for operator in d20.operations:
        if operator.op in ["adv", "dis"]:
            return False

    d20.operations.append(Operator(adv, Selector(None, count)))
    return True


def add_advantage_to_d20_in_expression(expr: ASTExpression, adv: AdvantageCategory, count: int) -> ASTExpression:
    """
    Add advantage to the d20 in an expression. This does not add advantage to
    the whole expression, rather it searches for the first (viable) d20 in the
    expression and adds advantage to that dice, if it doesn't already have it.

    Args:
        expr (ASTExpression): The expression to add it in.
        adv (AdvantageCategory): The advantage to add. Either 'adv' or 'dis'.
        count (int): The amount of times to roll.

    Raises:
        RollError: In case advantage could not be added.

    Returns:
        ASTExpression: The resulting expression with the advantage.
    """

    expr = expr.copy()  # Don't modify the original expression

    d20 = expr.find_d20()

    if d20 is None:
        raise RollError("Could not find a valid d20 to add advantage to.")

    if not _add_adv_operator(d20, adv, count):
        raise RollError(f"Could not add advantage to expression.")

    return expr


def apply_advantage_to_distribution(distribution: Distribution, adv: OperatorCategory | None, num: int | None):
    if adv is None:
        return distribution

    if num is None:
        num = 2

    if adv == "adv":
        return distribution.advantage(num)

    if adv == "dis":
        return distribution.disadvantage(num)

    raise RollError(f"Unknown advantage type: {adv}")
